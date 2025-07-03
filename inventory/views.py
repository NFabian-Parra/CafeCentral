
from django.shortcuts import render
from .models import Product # Importa el modelo Product
from django.contrib.auth.decorators import login_required
from .decorators import role_required

@login_required
@role_required(allowed_roles=['OWNER', 'ADMIN', 'EMPLOYEE'])
def product_list_view(request):
    """
    Vista para mostrar la lista de productos en el inventario.
    Esta vista será accesible para Empleados y roles superiores.
    """
    products = Product.objects.all().order_by('name') # Obtiene todos los productos ordenados por nombre
    context = {
        'products': products,
        'page_title': 'Inventario de Productos'
    }
    return render(request, 'inventory/product_list.html', context)

# Puedes añadir más vistas aquí en el futuro (ej. product_detail_view, sales_entry_view, etc.)