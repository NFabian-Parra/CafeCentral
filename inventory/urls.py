
from django.urls import path
from . import views # Importa las vistas de la aplicación inventory

app_name = 'inventory' # Define un namespace para esta app

urlpatterns = [
    # Ruta para la lista de productos (Se puede usar la función o la CBV)
    # path('products/', views.product_list_view, name='product_list'), # Opción con función
    # Rutas para el CRUD de Productos con CBV
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),

    # Aquí se añadirán más rutas para la app inventory (ej. sales)
]
