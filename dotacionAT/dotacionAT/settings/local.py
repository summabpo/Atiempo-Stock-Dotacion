from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

# if DEBUG:
#     INSTALLED_APPS += ["debug_toolbar"]
#     MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',  # Usar PostgreSQL en lugar de SQLite
#         'NAME': 'dotacion_at',  # Nombre de tu base de datos (por ejemplo, 'mi_proyecto')
#         'USER': 'postgres',  # Usuario de PostgreSQL
#         'PASSWORD': 'root',  # La contraseña del usuario 'postgres'
#         'HOST': 'localhost',  # PostgreSQL está corriendo localmente
#         'PORT': '5432',  # Puerto por defecto de PostgreSQL
#     }
# }

# if os.getenv('DB_ENGINE') == 'postgresql':
DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'dotacion_at'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'root'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
# else:
#     print("conexion else")
#     DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',  # Usar PostgreSQL en lugar de SQLite
#         'NAME': 'dotacion_at',  # Nombre de tu base de datos (por ejemplo, 'mi_proyecto')
#         'USER': 'postgres',  # Usuario de PostgreSQL
#         'PASSWORD': 'root',  # La contraseña del usuario 'postgres'
#         'HOST': 'localhost',  # PostgreSQL está corriendo localmente
#         'PORT': '5432',  # Puerto por defecto de PostgreSQL
#     }
# }


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Middleware de Debug Toolbar
# MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

# Solo permitir IPs locales
INTERNAL_IPS = ['127.0.0.1']

# Asegúrate de que Django puede acceder a los archivos estáticos de todas las aplicaciones
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# ]
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'applications/ciudades/static'),
]


CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']


# Deberia poner producción (por ejemplo, en un dominio real o con HTTPS), ahí sí deberías poner:
# CSRF_COOKIE_SECURE = True
# CSRF_TRUSTED_ORIGINS = ['https://tusitio.com']