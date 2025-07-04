
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
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