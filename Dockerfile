FROM python:alpine

COPY ./requirements.txt .

RUN apk update && apk add --no-cache nginx gcc musl-dev openldap-dev openssl git \
    && python -m pip install --no-cache-dir --no-warn-script-location --upgrade pip \
    && python -m pip install --no-cache-dir --no-warn-script-location --user -r requirements.txt \
    && apk del --no-cache gcc musl-dev

COPY ./conf/nginx/YARIK-management.conf /etc/nginx/http.d/YARIK-management.conf

RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log \
    && mkdir /usr/src/YARIK-management


WORKDIR /usr/src/YARIK-management

COPY ./src/. ./src/
COPY ./scripts/. ./scripts/

RUN chmod +x ./scripts/entrypoint.sh

WORKDIR /usr/src/YARIK-management/src

ENTRYPOINT ["/bin/sh", "/usr/src/YARIK-management/scripts/entrypoint.sh"]