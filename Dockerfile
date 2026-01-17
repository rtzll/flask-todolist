FROM python:3.14-alpine AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /code

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .
