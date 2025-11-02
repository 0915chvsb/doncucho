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

    path('', views.index, name='index'),
]