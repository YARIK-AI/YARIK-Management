#!/bin/sh

RUN_PORT="8080"
PROJECT_DIR=/usr/src/YARIK-management
SRC_DIR=$PROJECT_DIR/src

echo "### start django migrations ###"
cd $SRC_DIR
python manage.py makemigrations --force-color --no-input -v 3
python manage.py makemigrations --merge --no-input -v 3
python manage.py migrate --force-color --no-input -v 3
python manage.py createsuperuser --noinput
python manage.py collectstatic --noinput

cd /etc/nginx

echo "### generating secrets ###"
openssl genrsa 2048 > host.key
chmod 400 host.key
openssl req -new -x509 -nodes -sha256 -days 365 -key host.key -out host.cert \
 -subj "/C=RU/ST=Tatarstan/L=Kazan/O=TelInt/CN=www.example.com"

cd $SRC_DIR

echo "### starting nginx proxy ###"
nginx -g 'daemon on;'

mkdir /var/log/gunicorn

echo "### starting gunicorn http server ###"
#python -m gunicorn --bind "0.0.0.0:${RUN_PORT}" core.wsgi:application --log-level info \
# --access-logfile - --error-logfile - --capture-output

python manage.py runserver 0.0.0.0:8080

#while true; do echo hello; sleep 10;done