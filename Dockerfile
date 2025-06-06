# start from an official image
FROM python:3.11.4-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /opt/tax-latest

COPY requirements.txt .

RUN pip install -U pip

RUN pip install -r requirements.txt

COPY . .

RUN python manage.py migrate
RUN python manage.py collectstatic --no-input

CMD ["gunicorn", "core", "--bind", ":8000", "core.wsgi:application"]
# CMD ["gunicorn", "--chdir", "core", "--bind", ":8000", "core.wsgi:application", "--reload"]

# COPY manage.py .
# COPY core core

# RUN python manage.py collectstatic --noinput







# # set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# WORKDIR /app

# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser ./

# USER appuser


# RUN pip install --upgrade pip

# # install our dependencies
# COPY ./requirements.txt /app/requirements.txt

# RUN python -m pip install --no-cache-dir -r requirements.txt

# COPY . .

# # RUN python manage.py makemigrations --no-input

# # RUN python manage.py migrate --no-input 

# # RUN python manage.py collectstatic --no-input -v 2

# # expose the port 8000
# # CMD ['python', 'manage.py', 'runserver']

# EXPOSE 8000
# # define the default command to run when starting the container

# # CMD ["gunicorn", "--chdir", "core", "--bind", ":8000", "core.wsgi:application", "--reload"]

# # RUN python manage.py migrate

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# # runs the production server
# # ENTRYPOINT ["python", "./manage.py"]
# # CMD ["runserver", "0.0.0.0:8000"]
