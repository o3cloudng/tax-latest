FROM python:3.11-slim

WORKDIR /app

RUN groupadd -r celery && \
    useradd -r -g celery celery && \
    mkdir -p /app/static /app/media && \
    chown -R celery:celery /app

COPY --from=django /wheels /wheels
COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    # && pip install --no-cache /wheels/* \
    # && rm -rf /var/lib/apt/lists/* /wheels

COPY --chown=celery:celery . .

USER celery