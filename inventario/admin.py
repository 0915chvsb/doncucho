from django.contrib import admin
from .models import Producto, Venta, DetalleVenta

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')

class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_venta', 'cajero', 'total_venta')
    list_filter = ('fecha_venta', 'cajero')
    search_fields = ('id', 'cajero__username')
    readonly_fields = ('fecha_venta', 'cajero', 'total_venta')
    inlines = [DetalleVentaInline]

admin.site.register(Producto)
admin.site.register(Venta, VentaAdmin)