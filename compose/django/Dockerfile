# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app


RUN groupadd -r django && \
useradd -r -g django django && \
mkdir -p /app/static /app/media && \
chown -R django:django /app

COPY --from=builder /wheels /wheels
COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    && pip install --upgrade pip \
    libpq5 \
    # && pip install --no-cache /wheels/* \
    # && rm -rf /var/lib/apt/lists/* /wheels


COPY --chown=django:django . .

USER django

ENTRYPOINT ["/app/compose/django/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--worker-class", "gthread", "--log-file", "-", "config.wsgi:application"]