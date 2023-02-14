#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done

echo "PostgreSQL started"

python3 manage.py migrate --noinput

# Compile scss file and follow changes
sass --watch /src/upont/static/scss/styles.scss /src/upont/static/scss/styles.css &

# Start redis server
redis-server 1>/dev/null 2>&1 &

# Start celery
celery -A upont worker -l info --logfile=/var/log/celery.log --detach
celery -A upont beat --scheduler django_celery_beat.schedulers:DatabaseScheduler -l info --logfile=/var/log/celery-beat.log --detach

exec "$@"