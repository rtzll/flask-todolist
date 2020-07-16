FROM alpine:3.12

ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

RUN apk add --no-cache python3
RUN python3 -m ensurepip

ADD . /code
WORKDIR /code
RUN python3 -m pip install gunicorn
RUN python3 -m pip install -r requirements.txt
