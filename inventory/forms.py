from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Product, Role, Supplier, DailySalesSession, SaleItem
#import logging


#logger = logging.getLogger(__name__)

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('role',)
    
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

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 
                  'email', 'is_active', 'is_staff', 'is_superuser', 
                  'role', 'groups', 'user_permissions', 'last_login', 'date_joined'
                  )

# --- Formularios para la Interfaz de Usuario (Frontend) ---
### CBV significa Vistas Basadas en Clases (Class-Based Views)
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Define los campos que quieres que aparezcan en el formulario de tu producto
        # Puedes excluirlos o incluirlos explícitamente
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
        # Opcionalmente, se puede añadir widgets personalizados o etiquetas
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price_per_unit_from_supplier': forms.NumberInput(attrs={'step': '0.01'}),
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
        # Se puede incluir todos los campos o especificar cuáles quieres
        fields = [
            'name',
            'contact_person',
            'phone',
            'email',
            'address',
            'delivery_days',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'delivery_days': forms.TextInput(attrs={'placeholder': 'Ej: Lunes, Miércoles'}),
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
            'sale_date',
            'notes',
            # 'registered_by_user' no se incluye aquí, se asigna en la vista automáticamente
        ]
        widgets = {
            'sale_date': forms.DateInput(attrs={'type': 'date'}), # HTML5 date picker
            'notes': forms.Textarea(attrs={'rows': 4}),
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
#  añadir formularios para otros modelos aquí 