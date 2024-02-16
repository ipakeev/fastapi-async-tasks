FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_NO_INTERACTION=1

FROM base as builder

WORKDIR /app

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./
RUN python -m venv /venv

RUN poetry export --without=dev -f requirements.txt | /venv/bin/pip install -r /dev/stdin

FROM base as final

ENV PATH=/venv/bin:$PATH
ENV PYTHONPATH=/app:/venv:$PYTHONPATH

COPY --from=builder /venv /venv

WORKDIR /app

EXPOSE 8000
CMD uvicorn app.main:app --host=0.0.0.0 --port=8000 --reload