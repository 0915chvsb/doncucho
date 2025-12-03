#  DonCucho – Sistema Web de Inventario y Ventas Proyecto desarrollado en **Django** con integración de **Firebase Authentication**, orientado a la gestión de inventarios, ventas y control de lotes para pequeños comercios.

--

Características principales 
- Gestión de productos e inventario
- Registro de ventas y detalle de transacciones
- Control de lotes y proveedores
- Autenticación con **Firebase – Email/Password**
- Manejo seguro de variables de entorno
- Estructura modular y escalable basada en Django

---

Tecnologías utilizadas 
- **Django 4 / Python 3.10+**
- **Firebase Admin SDK**
- **SQLite / MySQL** (según configuración)
- HTML, CSS, Bootstrap - Git y GitHub para control de versiones

---

Estructura del proyecto 
├── config/ # Configuración principal del proyecto Django 
│ ├── settings.py # Variables, Firebase, DB, apps instaladas 
│ ├── urls.py # Rutas globales del sistema 
│ ├── wsgi.py # Configuración del servidor WSGI 
│ └── asgi.py # Configuración ASGI (si aplica) 
│ ├── inventario/ # App principal del sistema 
    │ ├── models.py # Modelos: Producto, Lote, Proveedor, Venta, etc. 
    │ ├── views.py # Lógica de vistas (inventario, ventas, login) 
    │ ├── urls.py # Rutas de la app 
    │ ├── forms.py # Formularios de Django (si los usas) 
    │ ├── templates/ # Archivos HTML del sistema 
    │ └── static/ # CSS, JS, imágenes 
│ ├── .env.example # Archivo plantilla para variables de entorno 
  ├── .gitignore # Exclusión de archivos de desarrollo 
  ├── manage.py # Punto de entrada del proyecto Django 
  └── requirements.txt # Dependencias necesarias para ejecutar el sistema
