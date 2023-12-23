FROM python:alpine

COPY ./requirements.txt .

RUN apk update && apk add --no-cache nginx gcc musl-dev openldap-dev openssl git \
    && python -m pip install --no-cache-dir --no-warn-script-location --upgrade pip \
    && python -m pip install --no-cache-dir --no-warn-script-location --user -r requirements.txt \
    && apk del --no-cache gcc musl-dev

COPY ./conf/nginx/djtest.conf /etc/nginx/http.d/djtest.conf

RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log \
    && mkdir /usr/src/djtest


WORKDIR /usr/src/djtest

COPY ./src/. ./src/
COPY ./scripts/. ./scripts/

RUN chmod +x ./scripts/entrypoint.sh

WORKDIR /usr/src/djtest/src

ENTRYPOINT ["/bin/sh", "/usr/src/djtest/scripts/entrypoint.sh"]