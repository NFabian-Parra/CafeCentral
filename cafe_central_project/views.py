from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F
from django.utils import timezone

# Importar los modelos necesarios desde el módulo inventory
from inventory.models import DailySalesSession, SaleItem, StockAlert, Product, CustomUser, Role

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