#!/bin/bash

# Export environment variables
export DJANGO_SETTINGS_MODULE=dotacionAT.settings.prod

# Apply migrations
echo 'Applying migrations...'
#python manage.py migrate --noinput

# Collect static files (ya ejecutado manualmente)
echo "Collecting static files..."
#python manage.py collectstatic --noinput

# Run server with Gunicorn
echo 'Running server...'
exec gunicorn --bind 0.0.0.0:8000 dotacionAT.wsgi:application --workers 3 --timeout 1200 --log-level debug
