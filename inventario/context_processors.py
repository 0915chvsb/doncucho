import os

def firebase_config(request):
    """
    Context processor para hacer las variables de Firebase disponibles en los templates
    """
    return {
        'FIREBASE_API_KEY': os.environ.get('FIREBASE_API_KEY', ''),
        'FIREBASE_AUTH_DOMAIN': os.environ.get('FIREBASE_AUTH_DOMAIN', ''),
        'FIREBASE_PROJECT_ID': os.environ.get('FIREBASE_PROJECT_ID', ''),
        'FIREBASE_STORAGE_BUCKET': os.environ.get('FIREBASE_STORAGE_BUCKET', ''),
        'FIREBASE_MESSAGING_SENDER_ID': os.environ.get('FIREBASE_MESSAGING_SENDER_ID', ''),
        'FIREBASE_APP_ID': os.environ.get('FIREBASE_APP_ID', ''),
        'FIREBASE_MEASUREMENT_ID': os.environ.get('FIREBASE_MEASUREMENT_ID', ''),
    }