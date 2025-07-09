
from django.urls import path
from . import views

app_name = 'inventory' # Define un namespace para esta app

urlpatterns = [
    # Ruta para la lista de productos (Se puede usar la función o la CBV)
    # path('products/', views.product_list_view, name='product_list'), # Opción con función
    
    # RUTAS para el CRUD de Productos con CBV
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    # RUTAS para el CRUD de Proveedores con CBV
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),

        # --- RUTAS para el CRUD de Sesiones de Venta ---
    path('sales/sessions/', views.DailySalesSessionListView.as_view(), name='dailysalessession_list'),
    path('sales/sessions/add/', views.DailySalesSessionCreateView.as_view(), name='dailysalessession_create'),
    path('sales/sessions/<int:pk>/', views.DailySalesSessionDetailView.as_view(), name='dailysalessession_detail'),
    path('sales/sessions/<int:pk>/edit/', views.DailySalesSessionUpdateView.as_view(), name='dailysalessession_update'),
    path('sales/sessions/<int:pk>/delete/', views.DailySalesSessionDeleteView.as_view(), name='dailysalessession_delete'),

    # --- RUTA para añadir SaleItem a una Sesión específica ---
    path('sales/sessions/<int:pk>/add_item/', views.SaleItemCreateView.as_view(), name='saleitem_create'),
    
    # --- RUTAS para la gestión de StockAlerts ---
    path('alerts/', views.StockAlertListView.as_view(), name='stockalert_list'),
    path('alerts/<int:pk>/resolve/', views.StockAlertUpdateView.as_view(), name='stockalert_resolve'),
    
    # --- RUTAS para la gestión de Roles ---
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/add/', views.RoleCreateView.as_view(), name='role_create'),
    path('roles/<int:pk>/', views.RoleDetailView.as_view(), name='role_detail'),
    path('roles/<int:pk>/edit/', views.RoleUpdateView.as_view(), name='role_update'),
    path('roles/<int:pk>/delete/', views.RoleDeleteView.as_view(), name='role_delete'),
    
    # --- RUTAS para la gestión de CustomUser ---
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/add/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
]
