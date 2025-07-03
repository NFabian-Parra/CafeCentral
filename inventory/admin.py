from django.contrib import admin
from .models import Role, CustomUser, Supplier, Product, StockAlert, DailySalesSession, SaleItem
from .forms import CustomUserCreationForm, CustomUserChangeForm # ¡Importa los nuevos formularios!
from django.contrib.auth.admin import UserAdmin # ¡Importa UserAdmin!

# Crea una clase CustomUserAdmin para personalizar el comportamiento en el panel de administración
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'is_staff', 'role'] # Muestra el rol en la lista
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}), # Añade el campo 'role' a la sección de fieldsets
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}), # Añade el campo 'role' al formulario de añadir usuario
    )

admin.site.register(CustomUser, CustomUserAdmin) # ¡Registra tu CustomUserAdmin!

# Registrar los demás modelos como de costumbre
admin.site.register(Role)
admin.site.register(Supplier)
admin.site.register(Product)
admin.site.register(StockAlert)
admin.site.register(DailySalesSession)
admin.site.register(SaleItem)