#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done

echo "PostgreSQL started"

python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput
python3 manage.py check --deploy
python3 manage.py test

exec "$@"