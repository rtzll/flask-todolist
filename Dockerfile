FROM python:3.12-alpine

RUN apk add build-base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ADD . /code
WORKDIR /code

# Install dependencies using uv
RUN uv sync --frozen --no-dev
RUN uv pip install gunicorn
