#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done

echo "PostgreSQL started"

python3 manage.py migrate --noinput

# Compile scss file and follow changes
sass --watch /src/upont/static/scss/styles.scss /src/upont/static/scss/styles.css &

exec "$@"