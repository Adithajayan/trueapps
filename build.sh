#!/bin/bash

apt-get update

apt-get install -y \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpango1.0-dev \
    libgdk-pixbuf-2.0-0 \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info




pip install -r requirements.txt


#python manage.py makemigrations --noinput
#
#
#python manage.py flush --noinput
python manage.py migrate --noinput


python manage.py collectstatic --noinput
python manage.py createsuperuser --noinput --username trueapps --email trueapps@gmail.com || true