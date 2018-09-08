FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7

RUN apk update \
    && apk upgrade \
    && apk add build-base gcc musl-dev python3-dev libffi-dev openssl-dev ca-certificates libffi-dev linux-headers

COPY ./config.json /app/config.json
COPY ./app /app
COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
