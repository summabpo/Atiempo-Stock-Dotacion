from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"


if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Middleware de Debug Toolbar
# MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

# Solo permitir IPs locales
INTERNAL_IPS = ['127.0.0.1']

# Asegúrate de que Django puede acceder a los archivos estáticos de todas las aplicaciones
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'applications/ciudades/static'),
]
