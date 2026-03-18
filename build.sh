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

#!/bin/bash


pip install -r requirements.txt


python manage.py flush --noinput

# Ippo migration run cheyyaam
python manage.py migrate --noinput

# Static files collect cheyyaam
python manage.py collectstatic --noinput

# Superuser undakkaam (Username 'admin' aakkunnathaanu nallath)
python manage.py createsuperuser --noinput --username admin --email trueapps@gmail.com || true