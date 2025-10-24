from .base import *
import os

DEBUG = False

# (Datos que estaba manehando en PythonAnywhere)
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000']

# 💾 Base de datos:
# Si existen variables de entorno de PostgreSQL, las usa.
# Si no, se mantiene en SQLite (útil para pruebas).


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
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / 'db.sqlite3',
#         }
#     }

# 📦 Archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Si usas una carpeta "static" en tu proyecto (además de las apps)
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Evita servir estáticos obsoletos (usa hashes)
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# (Opcional) Archivos de usuario, si los manejas
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 🔒 Seguridad adicional
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True