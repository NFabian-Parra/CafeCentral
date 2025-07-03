
from django.urls import path
from . import views # Importa las vistas de tu aplicación inventory

app_name = 'inventory' # Define un namespace para esta app

urlpatterns = [
    path('products/', views.product_list_view, name='product_list'),
    # Aquí se añadirá más rutas para la app inventory
]