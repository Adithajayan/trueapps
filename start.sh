#!/usr/bin/env bash


python manage.py migrate --fake staff zero


python manage.py migrate --fake customer zero


python manage.py migrate staff
python manage.py migrate customer


python manage.py migrate --fake-initial


python manage.py collectstatic --noinput
gunicorn config.wsgi:application