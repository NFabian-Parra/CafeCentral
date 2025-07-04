# inventory/admin.py
from django.contrib import admin
from .models import Role, CustomUser, Supplier, Product, StockAlert, DailySalesSession, SaleItem
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # Renombramos UserAdmin para evitar conflictos

# Crea una clase CustomUserAdmin para personalizar el comportamiento en el panel de administración
class CustomUserAdmin(BaseUserAdmin): # Heredamos del UserAdmin renombrado
    list_display = ['username', 'email', 'is_staff', 'role']

    # Sobrescribimos fieldsets para el formulario de EDICIÓN (ChangeForm)
    # Aquí, 'password' sí se usa para el enlace "Change password" en el admin.
    fieldsets = (
        (None, {'fields': ('username', 'password')}), 
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    # Sobrescribimos add_fieldsets para el formulario de CREACIÓN (CreationForm)
    # ¡IMPORTANTE!: NO incluyas 'password' ni 'password2' aquí.
    # El UserCreationForm ya los define, y UserAdmin sabe cómo manejarlos sin que tú los liste.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # ¡IMPORTANTE! Usamos los nombres de campo esperados por UserCreationForm
            # UserAdmin sabe cómo renderizar y procesar estos campos.
            'fields': ('username', 'password',), 
        }),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    # Especificamos qué formularios usar para cada acción
    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = CustomUserChangeForm
        return super().get_form(request, obj, **kwargs)

    def get_add_form(self, request, **kwargs):
        kwargs['form'] = CustomUserCreationForm
        return super().get_add_form(request, **kwargs)

# Registrar el CustomUser con el CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)

# Registrar los demás modelos 
admin.site.register(Role)
admin.site.register(Supplier)
admin.site.register(Product)
admin.site.register(StockAlert)
admin.site.register(DailySalesSession)
admin.site.register(SaleItem)