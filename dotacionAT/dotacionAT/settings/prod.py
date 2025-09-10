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
STATIC_URL = '/static/'

# IMPORTANTE: Asegúrate que esta ruta existe y es la misma que usaste en collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # si tienes carpeta "static" dentro del proyecto
# Si tienes archivos estáticos dentro de apps (como ya tienes), puedes dejar tus STATICFILES_DIRS en base.py
# Ajuste para producción: añade hashes a los archivos estáticos
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
