FROM python:3.11.4-slim

WORKDIR /opt/tax-latest 

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# RUN python manage.py migrate
RUN python manage.py collectstatic --no-input