from django.contrib import admin
from django.urls import path, include # <-- ¡IMPORTANTE: Añade 'include' aquí!
from inventario import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'), 
    path('firebase-check/', views.login_firebase_prueba, name='firebase_check'),
    
    # AÑADE ESTA LÍNEA CLAVE:
    # Esto le dice a Django que incluya todas las rutas estándar de login/logout/password reset
    path('accounts/', include('django.contrib.auth.urls')), 
]