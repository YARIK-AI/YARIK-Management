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

echo "### end django migrations ###"

echo "### start generating secrets ###"

cd /etc/nginx

openssl genrsa 2048 > host.key
chmod 400 host.key
openssl req -new -x509 -nodes -sha256 -days 365 -key host.key -out host.cert \
 -subj "/C=RU/ST=Tatarstan/L=Kazan/O=TelInt/CN=www.example.com"

cd $SRC_DIR

echo "### secrets was successfully generated ###"

echo "### start gunicorn http ###"

python -m gunicorn --bind "0.0.0.0:${RUN_PORT}" management_web_app.wsgi:application --daemon --log-level info \
 --access-logfile /var/log/gunicorn/access.log --error-logfile /var/log/gunicorn/error.log

mkdir /var/log/gunicorn

ln -sf /dev/stdout /var/log/gunicorn/access.log
ln -sf /dev/stderr /var/log/gunicorn/error.log


echo "### gunicorn http started ###"

echo "### start nginx daemon ###"

#while true; do echo hello; sleep 10;done

nginx -g 'daemon off; error_log /dev/stdout info;'