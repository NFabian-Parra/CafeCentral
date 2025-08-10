
from pyexpat.errors import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # Para CBV
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView # Importa las CBV
from django.views import View # Importa la clase base View para vistas personalizadas
from django.forms import inlineformset_factory # Para gestionar formularios relacionados
from django.utils import timezone # Para asignar la hora de resolución
from django.db import models # Para usar F() en consultas

from .models import Product, StockMovement, Supplier, CustomUser, DailySalesSession, SaleItem, StockAlert, Role
from .decorators import role_required # Tu decorador personalizado
# Importa los formularios de usuario adecuados
from .forms import (
    ProductForm, StockMovementForm, SupplierForm, DailySalesSessionForm, SaleItemForm,
    StockAlertForm, RoleForm, CustomUserCreationForm, CustomUserChangeForm
)

# product_list_view (función) antes de Opción con CBV
# @login_required
# @role_required(allowed_roles=['OWNER', 'ADMIN', 'EMPLOYEE'])
# def product_list_view(request):
#     """
#     Vista para mostrar la lista de productos en el inventario.
#     Esta vista será accesible para Empleados y roles superiores.
#     """
#     products = Product.objects.all().order_by('name') # Obtiene todos los productos ordenados por nombre
#     context = {
#         'products': products,
#         'page_title': 'Inventario de Productos'
#     }
#     return render(request, 'inventory/product_list.html', context)

# Vistas Basadas en Clases (CBV) para CRUD de Productos
# CBV significa Vistas Basadas en Clases en Django (Class-Based Views)
# Mixin para verificar el rol en CBV
class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles = []

    def test_func(self):
        # Asegúra que el usuario esté autenticado
        if not self.request.user.is_authenticated:
            return False
        # Verifica si el rol del usuario está en los roles permitidos
        return self.request.user.role and self.request.user.role.name in self.allowed_roles

    def handle_no_permission(self):
        # Redirige a la página de inicio o a una página de error de acceso denegado
        return redirect(reverse_lazy('home')) # O una URL de error más específica

# --- VISTAS BASADAS EN CLASES (CBV) para la gestión de CustomUser ---

class UserListView(RoleRequiredMixin, ListView):
    model = CustomUser
    template_name = 'inventory/user_list.html'
    context_object_name = 'users'
    allowed_roles = ['OWNER']
    
    def get_queryset(self):
        # Excluir al propio usuario logueado de la lista si no quieres que se auto-elimine/edite su propio rol.
        # Esto puede ser gestionado también por lógica en la plantilla.
        return CustomUser.objects.exclude(pk=self.request.user.pk).order_by('username')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Gestión de Usuarios'
        return context

class UserDetailView(RoleRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'inventory/user_detail.html'
    context_object_name = 'user_obj'
    allowed_roles = ['OWNER']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Detalles de Usuario: {self.object.username}"
        return context

class UserCreateView(RoleRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm # Usa el formulario de creación de usuario
    template_name = 'inventory/user_form.html'
    success_url = reverse_lazy('inventory:user_list')
    allowed_roles = ['OWNER']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Crear Nuevo Usuario'
        return context

class UserUpdateView(RoleRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm # Usa el formulario de cambio de usuario
    template_name = 'inventory/user_form.html'
    context_object_name = 'user_obj'
    success_url = reverse_lazy('inventory:user_list')
    allowed_roles = ['OWNER']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar Usuario'
        return context

    def form_valid(self, form):
        if self.request.user.is_owner() and self.object.pk == self.request.user.pk:
            # Si el OWNER intenta editar su propio rol, se podría añadir una validación extra.
            # Por ahora, se permite.
            pass 
        return super().form_valid(form)


class UserDeleteView(RoleRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'inventory/user_confirm_delete.html'
    context_object_name = 'user_obj' 
    success_url = reverse_lazy('inventory:user_list')
    allowed_roles = ['OWNER']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Eliminar Usuario'
        return context

    # prevenir que un OWNER se auto-elimine
    def post(self, request, *args, **kwargs):
        if self.get_object().pk == request.user.pk:
            messages.error(request, "No puedes eliminar tu propia cuenta.")
            return redirect('inventory:user_list') # Redirigir de vuelta a la lista de usuarios
        return super().post(request, *args, **kwargs)
    

class ProductListView(RoleRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/product_list.html' # Reutiliza la plantilla existente
    context_object_name = 'products'
    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Inventario de Productos'
        
        # Calcular estadísticas de productos
        products = self.get_queryset()
        
        # Contar productos con stock bajo
        context['productos_stock_bajo'] = products.filter(
            current_stock__lte=models.F('minimum_stock_level')
        ).count()
        
        # Contar productos con proveedor asignado
        context['productos_con_proveedor'] = products.filter(
            supplier__isnull=False
        ).count()
        
        return context


class ProductDetailView(RoleRequiredMixin, DetailView):
    model = Product
    template_name = 'inventory/product_detail.html'
    context_object_name = 'product'
    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE']


class ProductCreateView(RoleRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list') # Redirige a la lista después de crear
    allowed_roles = ['OWNER', 'ADMIN']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Crear Nuevo Producto'
        return context


class ProductUpdateView(RoleRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list')
    allowed_roles = ['OWNER', 'ADMIN']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar Producto'
        return context


class ProductDeleteView(RoleRequiredMixin, DeleteView):
    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('inventory:product_list')
    allowed_roles = ['OWNER', 'ADMIN']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Eliminar Producto'
        return context

# --- VISTAS BASADAS EN CLASES (CBV) para CRUD de Proveedores ---

class SupplierListView(RoleRequiredMixin, ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'
    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Lista de Proveedores'
        return context


class SupplierDetailView(RoleRequiredMixin, DetailView):
    model = Supplier
    template_name = 'inventory/supplier_detail.html'
    context_object_name = 'supplier'
    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Detalles del Proveedor'
        return context


class SupplierCreateView(RoleRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')
    allowed_roles = ['OWNER', 'ADMIN']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Crear Nuevo Proveedor'
        return context


class SupplierUpdateView(RoleRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')
    allowed_roles = ['OWNER', 'ADMIN']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar Proveedor'
        return context


class SupplierDeleteView(RoleRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_list')
    allowed_roles = ['OWNER', 'ADMIN']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Eliminar Proveedor'
        return context
    
# --- VISTAS BASADAS EN CLASES (CBV) para CRUD de Sesiones de Venta ---
class DailySalesSessionListView(RoleRequiredMixin, ListView):
    model = DailySalesSession
    template_name = 'inventory/dailysalessession_list.html'
    context_object_name = 'sessions'
    ordering = ['-sale_date'] # Ordenar por fecha más reciente primero
    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Sesiones de Ventas Diarias'
        return context


class DailySalesSessionDetailView(RoleRequiredMixin, DetailView):
    model = DailySalesSession
    template_name = 'inventory/dailysalessession_detail.html'
    context_object_name = 'session'
    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Detalles de Sesión - {self.object.sale_date.strftime('%Y-%m-%d')}"
        # Añade los ítems de venta relacionados a la sesión
        context['sale_items'] = self.object.sale_items.all()
        # Forma para añadir un nuevo ítem de venta a esta sesión
        context['sale_item_form'] = SaleItemForm()
        return context


class DailySalesSessionCreateView(RoleRequiredMixin, CreateView):
    model = DailySalesSession
    form_class = DailySalesSessionForm
    template_name = 'inventory/dailysalessession_form.html'
    success_url = reverse_lazy('inventory:dailysalessession_list')
    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE']

    def form_valid(self, form):
        # Asignar automáticamente el usuario logueado como 'registered_by_user'
        form.instance.registered_by_user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Crear Nueva Sesión de Venta'
        return context


class DailySalesSessionUpdateView(RoleRequiredMixin, UpdateView):
    model = DailySalesSession
    form_class = DailySalesSessionForm
    template_name = 'inventory/dailysalessession_form.html'
    success_url = reverse_lazy('inventory:dailysalessession_list')
    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar Sesión de Venta'
        return context


class DailySalesSessionDeleteView(RoleRequiredMixin, DeleteView):
    model = DailySalesSession
    template_name = 'inventory/dailysalessession_confirm_delete.html'
    success_url = reverse_lazy('inventory:dailysalessession_list')
    allowed_roles = ['OWNER', 'ADMIN']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Eliminar Sesión de Venta'
        return context


# --- Vista para añadir SaleItem a una DailySalesSession específica ---
# Esta vista será una clase View estándar porque el manejo de formsets
# o múltiples formularios es más complejo que un simple ModelForm de CBV.

class SaleItemCreateView(RoleRequiredMixin, View):
    # Por simplicidad, permitimos a empleados añadir ítems de venta
    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE']

    def post(self, request, pk):
        session = get_object_or_404(DailySalesSession, pk=pk)
        form = SaleItemForm(request.POST)

        if form.is_valid():
            sale_item = form.save(commit=False)
            sale_item.sale_session = session
            sale_item.save()
            return redirect('inventory:dailysalessession_detail', pk=pk)
        else:
            # Si el formulario no es válido, volvemos a la página de detalle con los errores
            # Esto es un poco más complejo porque se renderiza la página de detalle
            # con el contexto completo y el formulario con errores.
            # Para una solución rápida, podríamos redirigir con un mensaje de error (usando messages framework)
            # o pasar los errores a la URL como parámetros, pero lo ideal es renderizar.
            # Por ahora, simplemente redirigiremos de nuevo a la página de detalle.
            # Una mejora futura sería renderizar la plantilla de detalle con el formulario pre-llenado y errores.
            context = {
                'session': session,
                'sale_items': session.sale_items.all(),
                'sale_item_form': form, # Se pasa el formulario con errores
                'page_title': f"Detalles de Sesión - {session.sale_date.strftime('%Y-%m-%d')}"
            }
            return render(request, 'inventory/dailysalessession_detail.html', context)

# --- BASADAS EN CLASES (CBV) para la gestión de StockAlerts ---

class StockAlertListView(RoleRequiredMixin, ListView):
    model = StockAlert
    template_name = 'inventory/stockalert_list.html'
    context_object_name = 'alerts'
    ordering = ['-alert_timestamp']
    # Los empleados pueden ver las alertas, pero solo los admins/owners las resuelven.
    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE']

    def get_queryset(self):
        # Opcional:  filtrar para mostrar solo las alertas no resueltas por defecto
        # return StockAlert.objects.filter(resolved=False).order_by('-alert_timestamp')
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Alertas de Stock'
        context['active_alerts_count'] = StockAlert.objects.filter(resolved=False).count()
        return context


class StockAlertUpdateView(RoleRequiredMixin, UpdateView):
    model = StockAlert
    form_class = StockAlertForm
    template_name = 'inventory/stockalert_form.html'
    success_url = reverse_lazy('inventory:stockalert_list')
    # Solo OWNER y ADMIN pueden resolver alertas
    allowed_roles = ['OWNER', 'ADMIN']

    def form_valid(self, form):
        # Si la alerta se está marcando como resuelta, asigna el usuario y el timestamp
        if form.instance.resolved and not self.object.resolved: # Si cambia de no resuelta a resuelta
            form.instance.resolved_by_user = self.request.user
            form.instance.resolved_timestamp = timezone.now()
        elif not form.instance.resolved and self.object.resolved: # Si se desmarca como resuelta
            form.instance.resolved_by_user = None
            form.instance.resolved_timestamp = None
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alert'] = self.get_object() # Esto asegura que el objeto de alerta esté disponible como 'alert'
        context['page_title'] = 'Resolver Alerta de Stock'
        return context

# Consideración: Para editar/eliminar SaleItem, se puede usar un enfoque similar (UpdateView/DeleteView)
# o gestionar directamente desde la página de detalle de la sesión con JavaScript para una mejor UX.
# Por ahora, solo se maneja añadir.

# --- VISTAS BASADAS EN CLASES (CBV) para la gestión de Roles ---

class RoleListView(RoleRequiredMixin, ListView):
    model = Role
    template_name = 'inventory/role_list.html'
    context_object_name = 'roles'
    allowed_roles = ['OWNER']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Gestión de Roles'
        return context

class RoleDetailView(RoleRequiredMixin, DetailView):
    model = Role
    template_name = 'inventory/role_detail.html'
    context_object_name = 'role'
    allowed_roles = ['OWNER']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Detalles del Rol: {self.object.get_name_display()}"
        return context

class RoleCreateView(RoleRequiredMixin, CreateView):
    model = Role
    form_class = RoleForm
    template_name = 'inventory/role_form.html'
    success_url = reverse_lazy('inventory:role_list')
    allowed_roles = ['OWNER']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Crear Nuevo Rol'
        return context

class RoleUpdateView(RoleRequiredMixin, UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'inventory/role_form.html'
    success_url = reverse_lazy('inventory:role_list')
    allowed_roles = ['OWNER']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar Rol'
        return context

class RoleDeleteView(RoleRequiredMixin, DeleteView):
    model = Role
    template_name = 'inventory/role_confirm_delete.html'
    success_url = reverse_lazy('inventory:role_list')
    allowed_roles = ['OWNER']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Eliminar Rol'
        return context
    
# ... (Tu código existente hasta aquí) ...

# --- VISTAS BASADAS EN CLASES (CBV) para la gestión de StockMovement ---

class StockMovementListView(RoleRequiredMixin, ListView):
    model = StockMovement
    template_name = 'inventory/stockmovement_list.html'
    context_object_name = 'movements'
    ordering = ['-movement_date'] # Muestra los más recientes primero
    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE'] # Empleados pueden ver el historial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Historial de Movimientos de Stock'
        return context


class StockMovementCreateView(RoleRequiredMixin, CreateView):
    model = StockMovement
    form_class = StockMovementForm
    template_name = 'inventory/stockmovement_form.html'
    success_url = reverse_lazy('inventory:stockmovement_list')
    allowed_roles = ['OWNER', 'ADMIN'] # Solo OWNER y ADMIN pueden registrar movimientos de stock

    def form_valid(self, form):
        # Asignar automáticamente el usuario logueado
        form.instance.registered_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Registrar Nuevo Movimiento de Stock'
        return context

# Opcional: Si decido implementar Detail, Update, Delete para StockMovement:
# class StockMovementDetailView(RoleRequiredMixin, DetailView):
#     model = StockMovement
#     template_name = 'inventory/stockmovement_detail.html'
#     context_object_name = 'movement'
#     allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE']

# class StockMovementUpdateView(RoleRequiredMixin, UpdateView):
#     model = StockMovement
#     form_class = StockMovementForm
#     template_name = 'inventory/stockmovement_form.html'
#     success_url = reverse_lazy('inventory:stockmovement_list')
#     allowed_roles = ['OWNER', 'ADMIN']

# class StockMovementDeleteView(RoleRequiredMixin, DeleteView):
#     model = StockMovement
#     template_name = 'inventory/stockmovement_confirm_delete.html'
#     success_url = reverse_lazy('inventory:stockmovement_list')
#     allowed_roles = ['OWNER', 'ADMIN']
#     # Consideración: La eliminación de movimientos de stock puede tener implicaciones en la auditoría.
#     # Puede que quiera restringirla fuertemente o solo permitirla en circunstancias muy específicas.