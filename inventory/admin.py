from django.contrib import admin

# inventory/admin.py
from django.contrib import admin
from .models import Role, CustomUser, Supplier, Product, StockAlert, DailySalesSession, SaleItem

# Registrar los modelos para que aparezcan en el panel de administración
admin.site.register(Role)
admin.site.register(CustomUser)
admin.site.register(Supplier)
admin.site.register(Product)
admin.site.register(StockAlert)
admin.site.register(DailySalesSession)
admin.site.register(SaleItem)