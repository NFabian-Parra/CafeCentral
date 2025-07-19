from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone # Para fechas y horas
from decimal import Decimal # Importar Decimal para precisión en cálculos

# --- MODELOS DE ROLES Y USUARIOS ---

class Role(models.Model):
    """
    Define los roles de usuario personalizados (Propietario, Administrador, Empleado).
    """
    ROLE_CHOICES = (
        ('OWNER', 'Propietario'),
        ('ADMIN', 'Administrador'),
        ('EMPLOYEE', 'Empleado'),
    )
    name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['name']

    def __str__(self):
        return self.get_name_display() # Muestra el nombre legible del rol

class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser e incluye un campo de rol.
    """
    role = models.ForeignKey(Role, 
                             on_delete=models.SET_NULL,
                             null=True, 
                             blank=True,
                             related_name='users_with_role',
                             help_text="Rol del usuario en el sistema (Empleado, Administrador, Propietario).")

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['username']

    def __str__(self):
        return self.username

    # Métodos de conveniencia para verificar roles (útiles en la lógica de negocio)
    def is_owner(self):
        return self.role and self.role.name == 'OWNER'

    def is_admin(self):
        return self.role and self.role.name == 'ADMIN'

    def is_employee(self):
        return self.role and self.role.name == 'EMPLOYEE'

# --- MODELOS DE INVENTARIO ---

class Supplier(models.Model):
    """
    Representa a los proveedores de productos.
    """
    name = models.CharField(max_length=100, unique=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    delivery_days = models.CharField(max_length=255, blank=True, null=True,
                                     help_text="Ej: Lunes, Miércoles, Viernes")
    # Mantener created_at y updated_at para consistencia de auditoría si se necesitan.
    # Si no se usan en ningún sitio, podrían eliminarse, pero es buena práctica.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Representa un producto en el inventario del café.
    """
    UNIT_CHOICES = (
        ('kg', 'Kilogramo'),
        ('lb', 'Libra'),
        ('unit', 'Unidad'),
        ('liter', 'Litro'),
        ('pack', 'Paquete'),
        ('g', 'Gramo'),
        ('ml', 'Mililitro'),
    )

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True, help_text="Descripción detallada del producto.")
    unit_of_measurement = models.CharField(max_length=10, choices=UNIT_CHOICES)
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    minimum_stock_level = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                              help_text="Nivel mínimo de stock para generar una alerta.")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='products')
    price_per_unit_from_supplier = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                                        help_text="Precio de compra al proveedor.")
    last_updated = models.DateTimeField(auto_now=True) # Se actualiza automáticamente en cada guardado

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.current_stock} {self.get_unit_of_measurement_display()})" # Usar get_unit_of_measurement_display

    def save(self, *args, **kwargs):
        # Guardar el valor original de current_stock antes de la actualización
        # Esto es crucial para detectar si el stock ha cambiado
        original_stock = None
        if self.pk: # Si el objeto ya existe, obtenemos su estado actual de la base de datos
            try:
                original_product = Product.objects.get(pk=self.pk)
                original_stock = original_product.current_stock
            except Product.DoesNotExist:
                pass # Esto no debería pasar si self.pk existe, pero es un buen control

        super().save(*args, **kwargs) # Llama al método save original para guardar el producto

        # Lógica para crear o resolver alertas de stock DESPUÉS de guardar
        # Usamos Decimal para comparaciones precisas
        
        # 1. Lógica para CREAR alertas
        # Crea una alerta si el stock BAJA y está por debajo/igual al mínimo,
        # y si NO hay ya una alerta ACTIVA para este producto.
        # (Esto evita duplicados y alertas falsas al subir stock o guardar sin cambios relevantes).
        if (original_stock is not None and self.current_stock < original_stock and 
            self.current_stock <= self.minimum_stock_level):
            
            if not StockAlert.objects.filter(product=self, resolved=False).exists():
                StockAlert.objects.create(
                    product=self,
                    current_stock_at_alert=self.current_stock,
                    alert_timestamp=timezone.now()
                )
        
        # 2. Lógica para RESOLVER alertas
        # Resuelve alertas si el stock SUBE y SUPERA el nivel mínimo.
        if (original_stock is not None and self.current_stock > original_stock and
            self.current_stock > self.minimum_stock_level):
            
            active_alerts = StockAlert.objects.filter(product=self, resolved=False)
            for alert in active_alerts:
                alert.resolved = True
                alert.resolved_by_user = None # O podrías buscar un usuario 'sistema' si lo creas.
                alert.resolved_timestamp = timezone.now()
                alert.save()

class StockAlert(models.Model):
    """
    Registra las alertas de stock cuando un producto alcanza su nivel mínimo.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_alerts')
    alert_timestamp = models.DateTimeField(auto_now_add=True) # Se establece al crear la alerta
    current_stock_at_alert = models.DecimalField(max_digits=10, decimal_places=2)
    resolved = models.BooleanField(default=False)
    resolved_by_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='resolved_alerts')
    resolved_timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Alerta de Stock"
        verbose_name_plural = "Alertas de Stock"
        ordering = ['-alert_timestamp'] # Ordena las alertas más nuevas primero
        # CRUCIAL: Solo permite UNA alerta activa por producto a la vez
        unique_together = ('product', 'resolved') # Permite (product_id, False) una vez, y (product_id, True) varias veces.

    def __str__(self):
        status = "Resuelta" if self.resolved else "Activa"
        return f"Alerta: {self.product.name} - Stock: {self.current_stock_at_alert} ({status})"

# --- MODELOS DE VENTAS ---

class DailySalesSession(models.Model):
    """
    Representa un registro de ventas diarias o una sesión de ventas.
    """
    # Cambié 'unique=True' a una validación en clean() si necesitas múltiples sesiones por día
    # Si quieres una sola por día, mantenlo. Asumo que una por día es lo esperado para "Daily"
    sale_date = models.DateField(default=timezone.now, unique=True) 
    registered_by_user = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True,
                                           related_name='daily_sales_registered')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Si 'updated_at' es útil para auditoría de la sesión misma, podrías añadirla.
    # updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        verbose_name = "Sesión de Venta Diaria"
        verbose_name_plural = "Sesiones de Ventas Diarias"
        ordering = ['-sale_date']

    def __str__(self):
        # Aseguramos que registered_by_user no sea None
        user_display = self.registered_by_user.username if self.registered_by_user else 'N/A'
        return f"Ventas del {self.sale_date.strftime('%Y-%m-%d')} por {user_display}"

    @property
    def total_revenue(self):
        """Calcula el total de ingresos para esta sesión de venta."""
        # Usa aggregate para eficiencia
        return self.sale_items.aggregate(total=models.Sum('subtotal'))['total'] or Decimal('0.00')

class SaleItem(models.Model):
    """
    Representa un ítem individual vendido dentro de una DailySalesSession.
    """
    sale_session = models.ForeignKey(DailySalesSession, on_delete=models.CASCADE, related_name='sale_items')
    # Recomendación: on_delete=models.PROTECT para product. No borrar productos si hay ventas.
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_records') 
    quantity_sold = models.DecimalField(max_digits=10, decimal_places=2)
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2,
                                         help_text="Precio unitario del producto en el momento de la venta.")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False) # Se calculará

    class Meta:
        verbose_name = "Ítem de Venta"
        verbose_name_plural = "Ítems de Venta"
        # Impide vender el mismo producto dos veces en la misma sesión
        unique_together = ('sale_session', 'product') 
        ordering = ['sale_session__sale_date', 'product__name']

    def save(self, *args, **kwargs):
        """
        Calcula el subtotal antes de guardar y ajusta el stock del producto.
        """
        # Calcular subtotal antes de guardar
        self.subtotal = self.quantity_sold * self.price_at_sale

        # Lógica para ajustar el stock del producto
        if self.pk: # Si es una actualización de un SaleItem existente
            original_item = SaleItem.objects.get(pk=self.pk)
            # Diferencia neta en la cantidad vendida
            stock_change_amount = self.quantity_sold - original_item.quantity_sold
            # Revertir el stock original y aplicar el nuevo cambio
            self.product.current_stock -= stock_change_amount
        else: # Si es un nuevo SaleItem
            self.product.current_stock -= self.quantity_sold
        
        # Primero guardamos el SaleItem. Si el SaleItem tiene un PK nulo, Django lo creará.
        # Si tiene un PK, lo actualizará.
        super().save(*args, **kwargs) 
        
        # Despues de que SaleItem se ha guardado, guardamos el producto
        # Esto activa el Product.save() modificado, que manejará las alertas.
        self.product.save() # Llama al método save del Producto. No necesitamos update_fields aquí.

    def delete(self, *args, **kwargs):
        """
        Cuando se elimina un SaleItem, devuelve el stock al producto.
        """
        self.product.current_stock += self.quantity_sold
        self.product.save() # Llama al método save del Producto, que manejará las alertas.
        super().delete(*args, **kwargs)


    def __str__(self):
        return f"{self.quantity_sold} de {self.product.name} en Venta del {self.sale_session.sale_date}"

# --- MODELO PARA MOVIMIENTOS DE STOCK ---

class StockMovement(models.Model):
    """
    Registra los movimientos de stock (entradas o salidas) de un producto.
    """
    MOVEMENT_TYPE_CHOICES = (
        ('IN', 'Entrada (Compra, Devolución, Ajuste Positivo)'),
        ('OUT', 'Salida (Merma, Uso Interno, Ajuste Negativo)'),
    )

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='stock_movements',
                                help_text="Producto afectado por el movimiento de stock.")
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPE_CHOICES,
                                     help_text="Tipo de movimiento: Entrada o Salida.")
    quantity = models.DecimalField(max_digits=10, decimal_places=2,
                                   help_text="Cantidad de unidades que se mueven.")
    movement_date = models.DateTimeField(default=timezone.now,
                                         help_text="Fecha y hora del movimiento de stock.")
    description = models.TextField(blank=True, null=True,
                                   help_text="Notas o razón del movimiento (ej. 'Compra a Proveedor X', 'Merma por producto dañado').")
    registered_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='stock_movements_registered',
                                      help_text="Usuario que registró este movimiento.")

    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-movement_date', 'product__name']

    def __str__(self):
        return f"{self.get_movement_type_display()} de {self.quantity} {self.product.get_unit_of_measurement_display()} de {self.product.name} ({self.movement_date.strftime('%Y-%m-%d %H:%M')})"

    def save(self, *args, **kwargs):
        # Guardar el movimiento para obtener un PK si es nuevo
        super().save(*args, **kwargs)
        
        # Necesitamos la instancia más reciente del producto desde la base de datos
        # para evitar problemas de concurrencia si el stock ya cambió en otro lugar.
        product = Product.objects.get(pk=self.product.pk)

        if self.movement_type == 'IN':
            product.current_stock += self.quantity
        elif self.movement_type == 'OUT':
            if product.current_stock < self.quantity:
                print(f"Advertencia: Intentando reducir stock de {product.name} a negativo. Stock actual: {product.current_stock}, Cantidad a retirar: {self.quantity}")
                product.current_stock = Decimal('0.00') # Asegura que no baje de cero
            else:
                product.current_stock -= self.quantity
        
        # Guarda el producto actualizado. Esto activará el método save() del producto,
        # el cual ya contiene la lógica de `StockAlert`.
        product.save()

    def delete(self, *args, **kwargs):
        """
        Cuando se elimina un StockMovement, se revierte el cambio en el stock del producto.
        """
        product = Product.objects.get(pk=self.product.pk) # Obtener la instancia más reciente
        if self.movement_type == 'IN':
            # Si era una entrada, al eliminarla se resta la cantidad del stock
            product.current_stock -= self.quantity
        elif self.movement_type == 'OUT':
            # Si era una salida, al eliminarla se suma la cantidad al stock
            product.current_stock += self.quantity
        
        product.save() # Guarda el producto actualizado, lo que manejará las alertas.
        super().delete(*args, **kwargs)