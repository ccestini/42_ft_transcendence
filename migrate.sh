#!/bin/bash

python -m pip install Pillow
python -m pip install django-debug-toolbar

echo "Running migrate.sh script..."

python project/manage.py makemigrations myapp --noinput
python project/manage.py migrate --noinput

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /code/localhost.key \
    -out /code/localhost.crt \
    -subj "/C=US/ST=YourState/L=YourCity/O=YourOrganization/CN=localhost"

cp localhost.crt /code/project/certs/localhost.crt
cp localhost.key /code/project/certs/localhost.key

python project/manage.py collectstatic --noinput

python project/manage.py runsslserver 0.0.0.0:8000 --cert /code/localhost.crt --key /code/localhost.key

echo "SSL enabled. Starting the server..."
