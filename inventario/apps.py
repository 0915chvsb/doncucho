import os
from django.apps import AppConfig
from django.conf import settings

import firebase_admin
from firebase_admin import credentials

class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventario'

    def ready(self):
        if not firebase_admin._apps:
            try:
                cred_config = settings.FIREBASE_SERVICE_ACCOUNT
                
                cred = credentials.Certificate(cred_config)
                firebase_admin.initialize_app(cred)
                print("Firebase Admin SDK inicializado correctamente.")
            except Exception as e:
                print(f"ERROR: No se pudo inicializar Firebase Admin SDK. {e}")