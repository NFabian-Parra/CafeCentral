# populate_roles.py
import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafe_central_project.settings')
django.setup()

from inventory.models import Role, CustomUser

def create_initial_roles_and_assign_to_superuser():
    """
    Crea los roles de usuario si no existen y asigna el rol de Propietario al superusuario.
    """
    print("Creando o verificando roles iniciales...")

    # Lista de roles a crear
    roles_to_create = {
        'OWNER': 'Propietario del café, con acceso total al sistema.',
        'ADMIN': 'Administrador del sistema, gestiona inventario y ventas.',
        'EMPLOYEE': 'Empleado, solo puede consultar inventario y alertas.'
    }

    created_roles = {}
    for name, description in roles_to_create.items():
        role, created = Role.objects.get_or_create(name=name, defaults={'description': description})
        created_roles[name] = role
        if created:
            print(f" - Rol '{role.get_name_display()}' creado.")
        else:
            print(f" - Rol '{role.get_name_display()}' ya existe.")

    print("\nAsignando rol de Propietario al superusuario (si existe y no tiene rol)...")
    try:
        # Asume que el primer superusuario creado es el Propietario
        superuser = CustomUser.objects.filter(is_superuser=True).first()
        if superuser and not superuser.role:
            owner_role = created_roles.get('OWNER')
            if owner_role:
                superuser.role = owner_role
                superuser.save()
                print(f" - Rol 'Propietario' asignado a '{superuser.username}'.")
            else:
                print(" - Error: Rol 'Propietario' no encontrado para asignación.")
        elif superuser and superuser.role:
            print(f" - Superusuario '{superuser.username}' ya tiene el rol '{superuser.role.get_name_display()}'.")
        else:
            print(" - No se encontró ningún superusuario para asignar un rol.")

    except Exception as e:
        print(f"Error al asignar rol al superusuario: {e}")

    print("\nProceso de roles completado.")

if __name__ == '__main__':
    create_initial_roles_and_assign_to_superuser()