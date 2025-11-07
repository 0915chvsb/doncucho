from django.contrib import admin
from .models import Producto, Venta, DetalleVenta, Proveedor, Categoria, Lote

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ('producto', 'lote_origen', 'cantidad', 'precio_unitario', 'subtotal')
    can_delete = False

class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_venta', 'cajero', 'total_venta')
    list_filter = ('fecha_venta', 'cajero')
    search_fields = ('id', 'cajero__username')
    readonly_fields = ('fecha_venta', 'cajero', 'total_venta')
    inlines = [DetalleVentaInline]

class LoteInline(admin.TabularInline):
    model = Lote
    extra = 1
    fields = ('precio_compra', 'stock_lote', 'fecha_vencimiento')

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'categoria', 'precio', 'stock_total', 'stock_minimo')
    list_filter = ('categoria', 'proveedor')
    search_fields = ('nombre', 'codigo')
    inlines = [LoteInline]
    readonly_fields = ('stock_total',)

admin.site.register(Producto, ProductoAdmin)
admin.site.register(Venta, VentaAdmin)
admin.site.register(Proveedor)
admin.site.register(Categoria)
admin.site.register(Lote)