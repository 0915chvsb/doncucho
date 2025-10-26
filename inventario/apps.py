import os
from django.apps import AppConfig

import firebase_admin
from firebase_admin import credentials

class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventario'

    def ready(self):
        if not firebase_admin._apps:
            service_account_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                'serviceAccountKey.json'
            )
            
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK inicializado correctamente.")