from .base import *

DEBUG = False

ALLOWED_HOSTS = ['DanielYustres.pythonanywhere.com']  # usa tu dominio tal cual
CSRF_TRUSTED_ORIGINS = ['https://danielyustres.pythonanywhere.com']

# Usar la misma BD SQLite por ahora
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static
STATIC_URL = 'static/'

# IMPORTANTE: Asegúrate que esta ruta existe y es la misma que usaste en collectstatic
STATIC_ROOT = '/home/DanielYustres/Atiempo-Stock-Dotacion/dotacionAT/staticfiles'

# Si tienes archivos estáticos dentro de apps (como ya tienes), puedes dejar tus STATICFILES_DIRS en base.py