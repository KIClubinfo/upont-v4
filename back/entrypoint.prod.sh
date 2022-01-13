#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done

echo "PostgreSQL started"

python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput
python manage.py check --deploy

exec "$@"