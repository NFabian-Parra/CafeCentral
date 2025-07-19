from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm as BaseUserChangeForm
from .models import CustomUser, Product, Role, StockMovement, Supplier, DailySalesSession, SaleItem, StockAlert
from django.utils import timezone
#import logging


#logger = logging.getLogger(__name__)

class CustomUserCreationForm(UserCreationForm):
    # Formulario para crear usuarios.
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'role',)
    
    # # --- MÉTODO PARA DEPURACIÓN ---    
    # def clean(self):
    #     cleaned_data = super().clean()
    #     # Imprime los errores en la consola del servidor
    #     if self.errors:
    #         logger.error("Errores de validación en CustomUserCreationForm:")
    #         for field, errors in self.errors.items():
    #             for error in errors:
    #                 logger.error(f"Campo '{field}': {error}")
    #     else:
    #         logger.info("Formulario CustomUserCreationForm validado exitosamente.")
    #     return cleaned_data
    # # --- FIN DEL MÉTODO DEPURACIÓN ---

class CustomUserChangeForm(BaseUserChangeForm):
    # Formulario para editar usuarios.
    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 'role',
            'is_active', # Es útil para activar/desactivar usuarios
            # 'is_staff', 'is_superuser', 'groups', 'user_permissions', # Estos son típicamente solo para el superusuario/admin de Django
            # 'last_login', 'date_joined' # Estos son automáticos/de solo lectura
        )
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'role': 'Rol del Usuario',
            'is_active': 'Activo',
        }

# --- Formularios para la Interfaz de Usuario (Frontend) ---
### CBV significa Vistas Basadas en Clases (Class-Based Views)
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'unit_of_measurement',
            'current_stock',
            'minimum_stock_level',
            'price_per_unit_from_supplier',
            'supplier', 
            # 'last_updated' no se incluye porque Django lo gestiona automáticamente (auto_now)
        ]
        # Widgets con clases de Tailwind CSS
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50',
                'placeholder': 'Ej: Café Molido Premium'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50',
                'placeholder': 'Descripción detallada del producto'
            }),
            'unit_of_measurement': forms.Select(attrs={
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50'
            }),
            'current_stock': forms.NumberInput(attrs={
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50',
                'step': '0.01'
            }),
            'minimum_stock_level': forms.NumberInput(attrs={
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50',
                'step': '0.01'
            }),
            'price_per_unit_from_supplier': forms.NumberInput(attrs={
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50',
                'step': '0.01'
            }),
            'supplier': forms.Select(attrs={
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50'
            }),
        }
        labels = {
            'name': 'Nombre del Producto',
            'description': 'Descripción',
            'unit_of_measurement': 'Unidad de Medida',
            'current_stock': 'Stock Actual',
            'minimum_stock_level': 'Nivel Mínimo de Stock',
            'price_per_unit_from_supplier': 'Precio de Compra por Unidad',
            'supplier': 'Proveedor',
        }

# --- FORMULARIO PARA SUPPLIER ---
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            'name',
            'contact_person',
            'phone',
            'email',
            'address',
            'delivery_days',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50',
                'placeholder': 'Ej: Distribuidora de Café El Cafetal'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50',
                'placeholder': 'Ej: Juan Pérez'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50',
                'placeholder': 'Ej: +34 612 345 678'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50',
                'placeholder': 'Ej: contacto@elcafetal.com'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50',
                'placeholder': 'Dirección completa del proveedor'
            }),
            'delivery_days': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50',
                'placeholder': 'Ej: Lunes, Miércoles'
            }),
        }
        labels = {
            'name': 'Nombre del Proveedor',
            'contact_person': 'Persona de Contacto',
            'phone': 'Teléfono',
            'email': 'Correo Electrónico',
            'address': 'Dirección',
            'delivery_days': 'Días de Entrega',
        }
        
# --- FORMULARIO PARA DailySalesSession ---
class DailySalesSessionForm(forms.ModelForm):
    class Meta:
        model = DailySalesSession
        fields = [
            'sale_date', 'notes',
            # 'registered_by_user' no se incluye aquí, se asigna en la vista automáticamente
        ]
        widgets = {
            'sale_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50',
                'placeholder': 'Notas adicionales sobre esta sesión de ventas'
            }),
        }
        labels = {
            'sale_date': 'Fecha de la Sesión',
            'notes': 'Notas de la Sesión',
        }

# --- FORMULARIO PARA SaleItem (para añadir ítems individuales a una sesión) ---
class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity_sold', 'price_at_sale']
        widgets = {
            'quantity_sold': forms.NumberInput(attrs={'step': '0.01'}),
            'price_at_sale': forms.NumberInput(attrs={'step': '0.01'}),
        }
        labels = {
            'product': 'Producto',
            'quantity_sold': 'Cantidad Vendida',
            'price_at_sale': 'Precio de Venta por Unidad',
        }
    
    # El precio de venta por unidad no sea menor que el precio de compra
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        price_at_sale = cleaned_data.get('price_at_sale')

        if product and price_at_sale is not None:
            # Se puede añadir lógica para comparar con el price_per_unit_from_supplier si es relevante
            # Por ahora, nos aseguramos de que no sea negativo o cero
            if price_at_sale <= 0:
                self.add_error('price_at_sale', "El precio de venta debe ser mayor que cero.")
            
            # Ejemplo de validación contra el precio de compra
            if price_at_sale < product.price_per_unit_from_supplier:
                self.add_error('price_at_sale', f"El precio de venta ({price_at_sale}) no puede ser menor que el precio de compra ({product.price_per_unit_from_supplier}).")

        return cleaned_data                

# ---FORMULARIO PARA StockAlert ---
class StockAlertForm(forms.ModelForm):
    class Meta:
        model = StockAlert
        fields = ['resolved'] # Solo el campo 'resolved' será editable directamente
        widgets = {
            'resolved': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 rounded border-coffee-300 text-coffee-600 focus:ring-coffee-500'
            }),
        }
        labels = {
            'resolved': 'Marcar como Resuelta',
        }

# --- FORMULARIO PARA Role ---
class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description']
        labels = {
            'name': 'Nombre del Rol',
            'description': 'Descripción del Rol',
        }
        widgets = {
            'name': forms.Select(attrs={
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50',
                'placeholder': 'Descripción detallada de las responsabilidades y permisos de este rol'
            }),
        }
    
    # Opcional: Validación para el campo 'name' para asegurar que sea una de las opciones válidas
    def clean_name(self):
        name = self.cleaned_data['name']
        valid_names = [choice[0] for choice in Role.ROLE_CHOICES]
        if name not in valid_names:
            raise forms.ValidationError(f"El nombre del rol '{name}' no es una opción válida.")
        return name

# --- FORMULARIO PARA StockMovement ---
class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = [
            'product',
            'movement_type',
            'quantity',
            'description',
            # 'movement_date' se asignará automáticamente a timezone.now en la vista
            # 'registered_by' se asignará automáticamente al request.user en la vista
        ]
        widgets = {
            'product': forms.Select(attrs={
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50'
            }),
            'movement_type': forms.Select(attrs={
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50'
            }),
            'quantity': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0',
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring focus:ring-coffee-200 focus:ring-opacity-50',
                'placeholder': 'Explica el motivo de este movimiento de stock'
            }),
        }
        labels = {
            'product': 'Producto',
            'movement_type': 'Tipo de Movimiento',
            'quantity': 'Cantidad',
            'description': 'Descripción / Motivo',
        }

    def clean(self):
        cleaned_data = super().clean()
        movement_type = cleaned_data.get('movement_type')
        quantity = cleaned_data.get('quantity')
        product = cleaned_data.get('product')

        if quantity is not None and quantity <= 0:
            self.add_error('quantity', "La cantidad debe ser un valor positivo.")
        
        if movement_type == 'OUT' and product and quantity is not None:
            # Validar que no se retire más stock del disponible
            if product.current_stock < quantity:
                self.add_error('quantity', f"No hay suficiente stock de '{product.name}'. Stock actual: {product.current_stock} {product.get_unit_of_measurement_display()}.")

        return cleaned_data
