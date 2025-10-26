from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.conf import settings
from django.db import IntegrityError

import firebase_admin
from firebase_admin import credentials, auth
import os
import json
import pytz


if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"ATENCIÓN: Firebase Admin SDK no inicializado correctamente. {e}")


def index(request):
    if not request.user.is_authenticated:
        return redirect('login') 
    
    context = {
        'username': request.user.username,
        'is_admin': request.user.is_staff
    }
    return render(request, 'index.html', context)


@csrf_exempt 
def login_check_unsafe(request):
    return _login_verification_logic(request)


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
                        is_staff=True,
                        is_superuser=True
                    )
                    user.set_unusable_password() 
                    user.save()
                except IntegrityError:
                    user = User.objects.get(username=email)

            auth_login(request, user)
            
            return JsonResponse({'success': True}, status=200)

        except auth.InvalidIdTokenError as e:
            print(f"Error de Token Firebase: {e}")
            return JsonResponse({'error': 'Error de seguridad: Token inválido. La firma del token falló.'}, status=401)
        
        except Exception as e:
            print(f"Error interno en login: {e}")
            return JsonResponse({'error': f'Error interno del servidor (DEBUG). Mensaje: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido.'}, status=405)