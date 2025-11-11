from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.conf import settings
from django.db import IntegrityError, transaction
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.db.models import F
# from django.contrib import messages

import firebase_admin
from firebase_admin import credentials, auth
import os
import json
import pytz
from decimal import Decimal

from .models import Producto, Venta, DetalleVenta, Lote


if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"ATENCIÓN: Firebase Admin SDK no inicializado correctamente. {e}")


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
def index(request):
    if not request.user.is_authenticated:
        return redirect('login') 
    
    if not request.user.is_staff:
        return redirect('pos')

    context = {
        'username': request.user.username,
        'is_admin': request.user.is_staff
    }
    return render(request, 'index.html', context)


@csrf_exempt 
def _login_verification_logic(request):
    if request.method == 'POST':
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Token no proporcionado.'}, status=401)
        
        id_token = auth_header.split(' ')[1]
        
        try:
            decoded_token = auth.verify_id_token(id_token, clock_skew_seconds=10) 
            email = decoded_token.get('email')
            
            if not email:
                 return JsonResponse({'error': 'Token no contiene un email válido.'}, status=401)

            try:
                user = User.objects.get(username=email)
            except User.DoesNotExist:
                try:
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        is_staff=False,
                        is_superuser=False
                    )
                    user.set_unusable_password() 
                    user.save()
                except IntegrityError:
                    user = User.objects.get(username=email)

            auth_login(request, user)
            
            return JsonResponse({'success': True}, status=200)

        except auth.InvalidIdTokenError as e:
            print(f"Error de Token Firebase: {e}")
            return JsonResponse({'error': 'Error de seguridad: Token inválido. (La firma del token falló).'}, status=401)
        
        except Exception as e:
            print(f"Error interno en login: {e}")
            return JsonResponse({'error': f'Error interno del servidor (DEBUG). Mensaje: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido.'}, status=405)

@login_required
def vista_pos(request):
    return render(request, 'pos/pos_index.html')

@login_required
def api_buscar_producto(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            codigo = data.get('codigo')
            
            if not codigo:
                return JsonResponse({'error': 'No se proporcionado código.'}, status=400)

            producto = Producto.objects.get(codigo=codigo)
            
            lote_disponible = producto.lotes.filter(
                stock_lote__gt=0, 
                fecha_vencimiento__gt=timezone.now()
            ).order_by('fecha_vencimiento').first()

            if not lote_disponible:
                return JsonResponse({'error': 'Producto sin stock disponible o vencido.'}, status=404)

            producto_data = {
                'id': producto.id,
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'stock': lote_disponible.stock_lote,
                'lote_id': lote_disponible.id
            }
            return JsonResponse(producto_data, status=200)
            
        except Producto.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Método no permitido.'}, status=405)

@login_required
@admin_required
def control_inventario(request):
    productos = Producto.objects.all()
    context = {
        'productos': productos
    }
    return render(request, 'inventario/control_inventario.html', context)

@login_required
@admin_required
def inventario_crear(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')
        stock_minimo = request.POST.get('stock_minimo')
        
        try:
            Producto.objects.create(
                codigo=codigo,
                nombre=nombre,
                precio=precio,
                stock_minimo=stock_minimo
            )
            return redirect('control_inventario')
        except IntegrityError:
            pass 
        except Exception as e:
            pass 
            
    return render(request, 'inventario/inventario_form.html')

@login_required
@admin_required
def inventario_editar(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        producto.codigo = request.POST.get('codigo')
        producto.nombre = request.POST.get('nombre')
        producto.precio = request.POST.get('precio')
        producto.stock_minimo = request.POST.get('stock_minimo')
        
        try:
            producto.save()
            return redirect('control_inventario')
        except IntegrityError:
            pass 
        except Exception as e:
            pass
            
    context = {
        'producto': producto
    }
    return render(request, 'inventario/inventario_form.html', context)

@login_required
@admin_required
def inventario_eliminar(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    return redirect('control_inventario')

@login_required
@csrf_exempt
def api_finalizar_venta(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            carrito = data.get('carrito')
            total_venta = 0
            
            detalles_venta = []
            
            with transaction.atomic():
                
                nueva_venta = Venta.objects.create(
                    cajero=request.user,
                    total_venta=0 
                )

                for codigo, item in carrito.items():
                    producto = Producto.objects.get(codigo=codigo)
                    cantidad_a_vender = item['cantidad']
                    
                    lotes_disponibles = producto.lotes.filter(
                        stock_lote__gt=0, 
                        fecha_vencimiento__gt=timezone.now()
                    ).order_by('fecha_vencimiento')
                    
                    for lote in lotes_disponibles:
                        if cantidad_a_vender == 0:
                            break
                        
                        cantidad_lote = min(lote.stock_lote, cantidad_a_vender)
                        
                        lote.stock_lote -= cantidad_lote
                        lote.save()
                        
                        subtotal = producto.precio * cantidad_lote
                        total_venta += subtotal
                        
                        detalles_venta.append(
                            DetalleVenta(
                                venta=nueva_venta,
                                producto=producto,
                                lote_origen=lote,
                                cantidad=cantidad_lote,
                                precio_unitario=producto.precio,
                                subtotal=subtotal
                            )
                        )
                        cantidad_a_vender -= cantidad_lote
                    
                    if cantidad_a_vender > 0:
                        raise Exception(f"Stock insuficiente para {producto.nombre}")

                nueva_venta.total_venta = total_venta
                nueva_venta.save()
                
                DetalleVenta.objects.bulk_create(detalles_venta)
            
            return JsonResponse({'success': 'Venta registrada y stock actualizado.'}, status=200)
            
        except Producto.DoesNotExist:
            return JsonResponse({'error': 'Un producto en el carrito no existe.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)

@login_required
@admin_required
def reporte_stock_bajo(request):
    productos = Producto.objects.all()
    productos_bajos = [p for p in productos if p.stock_total <= p.stock_minimo]
    
    context = {
        'productos': productos_bajos
    }
    return render(request, 'inventario/reporte_stock.html', context)

@login_required
@admin_required
def reporte_ventas(request):
    ventas = Venta.objects.all().order_by('-fecha_venta').prefetch_related('detalles', 'detalles__producto')
    context = {
        'ventas': ventas
    }
    return render(request, 'inventario/reporte_ventas.html', context)

