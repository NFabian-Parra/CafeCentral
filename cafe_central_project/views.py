from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F
from django.utils import timezone
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages

# Importar los modelos necesarios desde el módulo inventory
from inventory.models import DailySalesSession, SaleItem, StockAlert, Product, CustomUser, Role
from inventory.forms import CustomUserCreationForm

class SignupView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        # Guardar el nuevo usuario
        response = super().form_valid(form)
        
        # Iniciar sesión automáticamente después del registro
        login(self.request, self.object)
        
        # Mensaje de éxito
        messages.success(self.request, f'¡Bienvenido/a {self.object.username}! Tu cuenta ha sido creada exitosamente.')
        
        return response
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Aplicar estilos de Tailwind CSS a los campos de contraseña
        form.fields['password1'].widget.attrs.update({
            'class': 'pl-10 block w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring-coffee-500 sm:text-sm',
            'placeholder': '••••••••'
        })
        form.fields['password2'].widget.attrs.update({
            'class': 'pl-10 block w-full rounded-md border-coffee-300 shadow-sm focus:border-coffee-500 focus:ring-coffee-500 sm:text-sm',
            'placeholder': '••••••••'
        })
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Registro - CafeCentral'
        return context
    
    def dispatch(self, request, *args, **kwargs):
        # Redirigir a la página de inicio si el usuario ya está autenticado
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


@login_required
def home(request):
    context = {
        'project_name': 'CafeCentral',
        'page_title': 'Inicio - Dashboard'
    }

    user = request.user

    # Datos generales para todos los usuarios autenticados
    total_products = Product.objects.count()
    active_stock_alerts = StockAlert.objects.filter(resolved=False)
    active_stock_alerts_count = active_stock_alerts.count()
    
    # Productos con stock bajo: current_stock menor o igual al minimum_stock_level
    products_low_stock_queryset = Product.objects.filter(current_stock__lte=F('minimum_stock_level'))
    products_low_stock_count = products_low_stock_queryset.count()

    context.update({
        'total_products': total_products,
        'active_stock_alerts_count': active_stock_alerts_count,
        'products_low_stock_count': products_low_stock_count,
        'active_stock_alerts_list': active_stock_alerts, # Renombrado para claridad en la plantilla
        'products_low_stock_list': products_low_stock_queryset, # Renombrado para claridad en la plantilla
    })

    # Datos específicos para OWNERs y ADMINs
    if user.is_owner() or user.is_admin():
        today = timezone.localdate()
        
        # Ventas de hoy
        today_sales_session = DailySalesSession.objects.filter(sale_date=today).first()
        total_revenue_today = 0
        total_items_sold_today = 0
        if today_sales_session:
            sales_data = today_sales_session.sale_items.aggregate(
                total_revenue=Sum('subtotal'),
                total_quantity=Sum('quantity_sold')
            )
            total_revenue_today = sales_data['total_revenue'] or 0
            total_items_sold_today = sales_data['total_quantity'] or 0
        
        # Conteo de usuarios por rol (OWNER, ADMIN, EMPLOYEE)
        owner_count = CustomUser.objects.filter(role__name='OWNER').count()
        admin_count = CustomUser.objects.filter(role__name='ADMIN').count()
        employee_count = CustomUser.objects.filter(role__name='EMPLOYEE').count()

        context.update({
            'total_revenue_today': total_revenue_today,
            'total_items_sold_today': total_items_sold_today,
            'owner_count': owner_count,
            'admin_count': admin_count,
            'employee_count': employee_count,
            'today_sales_session_exists': today_sales_session is not None,
            'today_sales_session_pk': today_sales_session.pk if today_sales_session else None,
        })
    
    return render(request, 'home.html', context)