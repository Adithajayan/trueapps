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


# Force migration for staff app during build
python manage.py makemigrations staff --noinput

# Apply the migration to Postgres
python manage.py migrate --noinput


python manage.py collectstatic --noinput
python manage.py createsuperuser --noinput --username trueapps --email trueapps@gmail.com || true