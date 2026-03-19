#!/usr/bin/env bash

python manage.py migrate --fake-initial
python manage.py collectstatic --noinput
gunicorn config.wsgi:application