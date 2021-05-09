FROM python:3-alpine

RUN apk add build-base

ADD . /code
WORKDIR /code

RUN pip install gunicorn
RUN pip install -r requirements.txt
