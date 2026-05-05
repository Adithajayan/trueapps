#!/usr/bin/env bash

python manage.py makemigrations staff --noinput

python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn config.wsgi:application