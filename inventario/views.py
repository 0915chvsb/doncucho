from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings
import firebase_admin
from firebase_admin import credentials
try:
    cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT)
    firebase_admin.initialize_app(cred)
    FIREBASE_INITIALIZED = True
except Exception as e:
    print(f"ERROR: No se pudo inicializar Firebase. Asegúrate de que '{settings.FIREBASE_SERVICE_ACCOUNT}' exista en la raíz.")
    print(e)
    FIREBASE_INITIALIZED = False


def index(request):
    return HttpResponse("Hola Mundo (v1.3 - con FIREBASE configurado)")

def login_firebase_prueba(request):
    if not FIREBASE_INITIALIZED:
        return HttpResponse("Error: Firebase no se pudo conectar. Revisa la clave JSON.", status=500)

    return HttpResponse("Firebase está inicializado y listo para autenticar tokens.", status=200)