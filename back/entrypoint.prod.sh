#!/bin/sh

# Start celery
celery -A upont worker -l info --logfile=/var/log/celery.log --detach
celery -A upont beat --scheduler django_celery_beat.schedulers:DatabaseScheduler -l info --logfile=/var/log/celery-beat.log --detach

# Prepare static files
python3 manage.py check --deploy

echo "Waiting for webinstaller to finish..."
while ping -c 1 webinstaller > /dev/null; do
    sleep 0.1
done
echo "Webinstaller exited."

echo "Copying static files..."
python3 manage.py collectstatic --noinput

echo "Check if PostgreSQL started..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done
echo "PostgreSQL started."

python3 manage.py migrate --noinput

# Compile scss files
sass --watch /src/upont/static/scss/styles.scss /src/upont/static/scss/styles.css &

exec "$@"
