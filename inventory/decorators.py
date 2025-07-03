from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
# from django.urls import reverse

def role_required(allowed_roles=None):
    """
    Decorador para restringir el acceso a vistas basado en el rol del usuario.
    Ejemplo: @role_required(allowed_roles=['OWNER', 'ADMIN'])
    """
    if allowed_roles is None:
        allowed_roles = []

    def check_role(user):
        # Se asegura de que el usuario tenga un rol y que su nombre esté en los roles permitidos
        if user.is_authenticated and user.role and user.role.name in allowed_roles:
            return True
        # Si el usuario no tiene el rol permitido, redirige Por ahora a la página de inicio
        return False # Retorna False para que user_passes_test maneje la redirección a LOGIN_URL

    return user_passes_test(check_role, login_url='home') # Redirige a 'home' si no cumple el rol