# -------- Stage 1: Build base --------
FROM python:3.11.4-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# -------- Stage 2: Final runtime --------
FROM python:3.11.4-slim

WORKDIR /app/tax-service

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
RUN pip install --no-index --find-links=/wheels /wheels/*

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
