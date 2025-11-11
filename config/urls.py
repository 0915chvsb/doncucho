from django.contrib import admin
from django.urls import path, include
from inventario import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/login-check/', views._login_verification_logic, name='login_check'),
    
    path('pos/', views.vista_pos, name='pos'),
    path('api/buscar-producto/', views.api_buscar_producto, name='api_buscar_producto'),
    path('api/finalizar-venta/', views.api_finalizar_venta, name='api_finalizar_venta'),

    path('inventario/', views.control_inventario, name='control_inventario'),
    path('inventario/nuevo/', views.inventario_crear, name='inventario_crear'),
    path('inventario/editar/<int:id>/', views.inventario_editar, name='inventario_editar'),
    path('inventario/eliminar/<int:id>/', views.inventario_eliminar, name='inventario_eliminar'),
    path('inventario/reporte-stock/', views.reporte_stock_bajo, name='reporte_stock_bajo'),
    path('inventario/reporte-ventas/', views.reporte_ventas, name='reporte_ventas'),

    path('', views.index, name='index'),
]