"""
WSGI config for dotacionAT project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dotacionAT.settings.local')

# application = get_wsgi_application()

import os
import sys

# Añadimos las rutas al proyecto
project_home = '/home/DanielYustres/Atiempo-Stock-Dotacion'
if project_home not in sys.path:
    sys.path.append(project_home)

project_path = '/home/DanielYustres/Atiempo-Stock-Dotacion/dotacionAT'
if project_path not in sys.path:
    sys.path.append(project_path)

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dotacionAT.settings.prod')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()