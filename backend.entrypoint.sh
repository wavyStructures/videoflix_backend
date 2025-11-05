#!/bin/sh

set -e

echo "Warte auf PostgreSQL auf $DB_HOST:$DB_PORT..."

# -q für "quiet" (keine Ausgabe außer Fehlern)
# Die Schleife läuft, solange pg_isready *nicht* erfolgreich ist (Exit-Code != 0)
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -q; do
  echo "PostgreSQL ist nicht erreichbar - schlafe 1 Sekunde"
  sleep 1
done
echo "PostgreSQL ist bereit - fahre fort..."

if [ "$RUN" = "worker" ]; then
    echo "🎯 Starting RQ Worker..."
    exec python manage.py rqworker default
else
    echo "📦 Running migrations for backend..."
    python manage.py collectstatic --noinput
    python manage.py makemigrations
    python manage.py migrate

    echo "👑 Ensuring superuser exists..."
    python manage.py shell <<EOF

import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpassword')

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser '{username}'...")
    # Korrekter Aufruf: username hier übergeben
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created.")
else:
    print(f"Superuser '{username}' already exists.")
EOF

    echo "🚀 Starting Gunicorn Server..."
    # exec gunicorn core.wsgi:application --bind 0.0.0.0:8000

    exec gunicorn core.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 3 \
        --log-level debug \
        --timeout 120
    
fi


