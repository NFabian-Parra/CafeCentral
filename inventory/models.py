# inventory/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone # Para fechas y horas

# --- MODELOS DE ROLES Y USUARIOS ---
# Django ya tiene un sistema de usuario robusto. Lo extenderemos para nuestros roles.

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

# Extendemos el modelo de usuario por defecto de Django para añadir el campo de rol.
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
        ('g', 'Gramo'), # Añadido para mayor granularidad si es necesario
        ('ml', 'Mililitro'), # Añadido
    )

    name = models.CharField(max_length=100, unique=True)
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
        return f"{self.name} ({self.current_stock} {self.unit_of_measurement})"

class StockAlert(models.Model):
    """
    Registra las alertas de stock cuando un producto alcanza su nivel mínimo.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_alerts')
    alert_timestamp = models.DateTimeField(auto_now_add=True) # Se establece al crear la alerta
    current_stock_at_alert = models.DecimalField(max_digits=10, decimal_places=2)
    resolved = models.BooleanField(default=False)
    resolved_by_user = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='resolved_alerts') # 'CustomUser' para referenciar el modelo como cadena
    resolved_timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Alerta de Stock"
        verbose_name_plural = "Alertas de Stock"
        ordering = ['-alert_timestamp'] # Ordena las alertas más nuevas primero

    def __str__(self):
        status = "Resuelta" if self.resolved else "Activa"
        return f"Alerta: {self.product.name} - Stock: {self.current_stock_at_alert} ({status})"

# --- MODELOS DE VENTAS ---

class DailySalesSession(models.Model):
    """
    Representa un registro de ventas diarias o una sesión de ventas.
    """
    sale_date = models.DateField(default=timezone.now, unique=True) # Una sesión por día
    registered_by_user = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True,
                                           related_name='daily_sales_registered') # 'CustomUser' como cadena
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Sesión de Venta Diaria"
        verbose_name_plural = "Sesiones de Ventas Diarias"
        ordering = ['-sale_date']

    def __str__(self):
        return f"Ventas del {self.sale_date.strftime('%Y-%m-%d')} por {self.registered_by_user.username if self.registered_by_user else 'N/A'}"

    @property
    def total_revenue(self):
        """Calcula el total de ingresos para esta sesión de venta."""
        return self.sale_items.aggregate(total=models.Sum('subtotal'))['total'] or 0

class SaleItem(models.Model):
    """
    Representa un ítem individual vendido dentro de una DailySalesSession.
    """
    sale_session = models.ForeignKey(DailySalesSession, on_delete=models.CASCADE, related_name='sale_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sale_records')
    quantity_sold = models.DecimalField(max_digits=10, decimal_places=2)
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2,
                                        help_text="Precio unitario del producto en el momento de la venta.")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False) # Se calculará

    class Meta:
        verbose_name = "Ítem de Venta"
        verbose_name_plural = "Ítems de Venta"
        unique_together = ('sale_session', 'product') # No se puede vender el mismo producto dos veces en la misma sesión
        ordering = ['sale_session__sale_date', 'product__name'] # Ordenar por fecha y luego por producto

    def save(self, *args, **kwargs):
        """
        Calcula el subtotal antes de guardar y actualiza el stock del producto.
        """
        # Calcular subtotal antes de guardar
        self.subtotal = self.quantity_sold * self.price_at_sale

        # Detectar cambios en la cantidad vendida para ajustar el stock
        if self.pk: # Si es una actualización de un SaleItem existente
            original_item = SaleItem.objects.get(pk=self.pk)
            stock_change = self.quantity_sold - original_item.quantity_sold
        else: # Si es un nuevo SaleItem
            stock_change = self.quantity_sold

        super().save(*args, **kwargs) # Guardamos el SaleItem primero para asegurar el PK

        # Ahora actualizamos el stock del producto
        self.product.current_stock -= stock_change
        self.product.save(update_fields=['current_stock', 'last_updated'])

        # Lógica para alerta de stock (podría ser un signal o una función externa)
        # Para el MVP, lo ponemos aquí por simplicidad.
        if self.product.current_stock <= self.product.minimum_stock_level:
            # Revisa si ya hay una alerta activa no resuelta para este producto
            if not StockAlert.objects.filter(product=self.product, resolved=False).exists():
                StockAlert.objects.create(
                    product=self.product,
                    current_stock_at_alert=self.product.current_stock
                )


    def delete(self, *args, **kwargs):
        """
        Cuando se elimina un SaleItem, devuelve el stock al producto.
        """
        self.product.current_stock += self.quantity_sold
        self.product.save(update_fields=['current_stock', 'last_updated'])
        # Considerar si la eliminación de un SaleItem debería resolver una alerta existente
        # Esto es lógica de negocio que se podría refinar. Por ahora, no resuelve automáticamente.
        super().delete(*args, **kwargs)


    def __str__(self):
        return f"{self.quantity_sold} de {self.product.name} en Venta del {self.sale_session.sale_date}"
