FROM python:3.11.4-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .





# # start from an official image
# FROM python:3.11.4-slim

# ENV PYTHONUNBUFFERED 1
# ENV PYTHONDONTWRITEBYTECODE 1

# WORKDIR /opt/tax-latest

# COPY requirements.txt .

# RUN pip install -U pip

# RUN pip install -r requirements.txt

# COPY . .

# RUN python manage.py migrate
# RUN python manage.py collectstatic --no-input

# CMD ["gunicorn", "core", "--bind", ":8000", "core.wsgi:application"]