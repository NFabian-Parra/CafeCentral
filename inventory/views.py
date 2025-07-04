
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # Para CBV
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView # Importa las CBV
from django.views import View # Importa la clase base View para vistas personalizadas
from django.forms import inlineformset_factory # Para gestionar formularios relacionados

from .models import Product, Supplier, CustomUser, DailySalesSession, SaleItem
from .decorators import role_required # Tu decorador personalizado
from .forms import ProductForm, SupplierForm, DailySalesSessionForm, SaleItemForm

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
        # Asegúrate de que el usuario esté autenticado
        if not self.request.user.is_authenticated:
            return False
        # Verifica si el rol del usuario está en los roles permitidos
        return self.request.user.role and self.request.user.role.name in self.allowed_roles

    def handle_no_permission(self):
        # Redirige a la página de inicio o a una página de error de acceso denegado
        return redirect(reverse_lazy('home')) # O una URL de error más específica


class ProductListView(RoleRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/product_list.html' # Reutilizamos la plantilla existente
    context_object_name = 'products'
    # Puedes añadir un título aquí para la plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Inventario de Productos'
        return context

    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE']


class ProductDetailView(RoleRequiredMixin, DetailView):
    model = Product
    template_name = 'inventory/product_detail.html' # Nueva plantilla
    context_object_name = 'product'
    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE']


class ProductCreateView(RoleRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm # Usa el formulario que acabamos de crear
    template_name = 'inventory/product_form.html' # Nueva plantilla para crear/editar
    success_url = reverse_lazy('inventory:product_list') # Redirige a la lista después de crear
    allowed_roles = ['OWNER', 'ADMIN'] # Solo OWNER y ADMIN pueden crear productos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Crear Nuevo Producto'
        return context


class ProductUpdateView(RoleRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html' # Reutiliza la plantilla de formulario
    success_url = reverse_lazy('inventory:product_list')
    allowed_roles = ['OWNER', 'ADMIN'] # Solo OWNER y ADMIN pueden actualizar productos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar Producto'
        return context


class ProductDeleteView(RoleRequiredMixin, DeleteView):
    model = Product
    template_name = 'inventory/product_confirm_delete.html' # Nueva plantilla para confirmar eliminación
    success_url = reverse_lazy('inventory:product_list')
    allowed_roles = ['OWNER', 'ADMIN'] # Solo OWNER y ADMIN pueden eliminar productos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Eliminar Producto'
        return context

# Puedes decidir si quieres reemplazar product_list_view (función) con ProductListView (clase)
# Por ahora, mantendremos ambas, pero eventualmente puedes usar solo la CBV.

# --- VISTAS BASADAS EN CLASES (CBV) para CRUD de Proveedores ---

class SupplierListView(RoleRequiredMixin, ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html' # Nueva plantilla
    context_object_name = 'suppliers'
    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE'] # Empleados pueden ver proveedores

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Lista de Proveedores'
        return context


class SupplierDetailView(RoleRequiredMixin, DetailView):
    model = Supplier
    template_name = 'inventory/supplier_detail.html' # Nueva plantilla
    context_object_name = 'supplier'
    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Detalles del Proveedor'
        return context


class SupplierCreateView(RoleRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm # Usa el formulario que acabamos de crear
    template_name = 'inventory/supplier_form.html' # Nueva plantilla para crear/editar
    success_url = reverse_lazy('inventory:supplier_list') # Redirige a la lista después de crear
    allowed_roles = ['OWNER', 'ADMIN'] # Solo OWNER y ADMIN pueden crear proveedores

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Crear Nuevo Proveedor'
        return context


class SupplierUpdateView(RoleRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html' # Reutiliza la plantilla de formulario
    success_url = reverse_lazy('inventory:supplier_list')
    allowed_roles = ['OWNER', 'ADMIN'] # Solo OWNER y ADMIN pueden actualizar proveedores

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar Proveedor'
        return context


class SupplierDeleteView(RoleRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'inventory/supplier_confirm_delete.html' # Nueva plantilla para confirmar eliminación
    success_url = reverse_lazy('inventory:supplier_list')
    allowed_roles = ['OWNER', 'ADMIN'] # Solo OWNER y ADMIN pueden eliminar proveedores

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
    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE'] # Empleados pueden ver sesiones

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
    template_name = 'inventory/dailysalessession_form.html' # plantilla para crear/editar
    success_url = reverse_lazy('inventory:dailysalessession_list')
    allowed_roles = ['OWNER', 'ADMIN', 'EMPLOYEE'] # Empleados pueden crear sesiones

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
    template_name = 'inventory/dailysalessession_confirm_delete.html' #
    success_url = reverse_lazy('inventory:dailysalessession_list')
    allowed_roles = ['OWNER', 'ADMIN'] # Solo OWNER y ADMIN pueden eliminar sesiones

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
            # Calcula el subtotal aquí o asegúrate que el save del modelo lo haga
            # El modelo ya tiene la lógica de save para subtotal y stock.
            sale_item.save()
            return redirect('inventory:dailysalessession_detail', pk=pk)
        else:
            # Si el formulario no es válido, volvemos a la página de detalle con los errores
            # Esto es un poco más complejo porque necesitamos renderizar la página de detalle
            # con el contexto completo y el formulario con errores.
            # Para una solución rápida, podríamos redirigir con un mensaje de error (usando messages framework)
            # o pasar los errores a la URL como parámetros, pero lo ideal es renderizar.
            # Por ahora, simplemente redirigiremos de nuevo a la página de detalle.
            # Una mejora futura sería renderizar la plantilla de detalle con el formulario pre-llenado y errores.
            context = {
                'session': session,
                'sale_items': session.sale_items.all(),
                'sale_item_form': form, # Pasamos el formulario con errores
                'page_title': f"Detalles de Sesión - {session.sale_date.strftime('%Y-%m-%d')}"
            }
            return render(request, 'inventory/dailysalessession_detail.html', context)

# Consideración: Para editar/eliminar SaleItem, se puede usar un enfoque similar (UpdateView/DeleteView)
# o gestionar directamente desde la página de detalle de la sesión con JavaScript para una mejor UX.
# Por ahora, solo se maneja añadir.
