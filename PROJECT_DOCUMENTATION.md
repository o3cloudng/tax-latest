# Project Documentation: Maximum Collection Project

## Introduction
The Maximum Collection Project is a Django-based web application designed to manage tax collection, payments, and agency operations efficiently.

## Technologies Used
- Python 3.x
- Django 5.0.4
- PostgreSQL
- Redis
- Celery
- Docker & Docker Compose
- Nginx
- HTMX
- TailwindCSS (crispy-tailwind)
- Paystack (Payment Gateway)
- Gunicorn
- Whitenoise (Static file serving)
- Sentry (Error tracking)

## Project Structure
The project is structured into several Django apps, each handling specific functionalities:
- `account`: User management and authentication.
- `agency`: Agency management and notifications.
- `payments`: Payment processing and wallet management.
- `tax`: Infrastructure management, demand notices, waivers, and remittances.
- `core`: Core utilities, middleware, and decorators.
- `helpers`: Common utilities and error handling.

## Email and Notification System
The project uses Celery tasks for asynchronous email sending:
- `send_email_func`: Sends plain text emails.
- `send_html_email`: Sends HTML formatted emails.
- `send_periodic_emails`: Sends periodic emails to users with HTML content.

Emails are configured using Django Anymail with Brevo (Sendinblue) as the email backend.

## Deployment and Infrastructure
The project uses Docker Compose for container orchestration, including:
- PostgreSQL database container.
- Redis container for caching and Celery broker.
- Celery worker and beat for asynchronous tasks.
- Flower for Celery monitoring.
- Nginx as a reverse proxy and static file server.

## Database Schema and Models
### Account App
- Custom user model with roles and company details.
- Admin settings for configurable parameters.

### Agency App
- Agency details and notifications management.

### Payments App
- User wallet management.
- Payment transactions with unique references.

### Tax App
- Infrastructure types and details.
- Demand notices with detailed financial calculations.
- Waivers and remittance management.

## Security Recommendations
- Implement secure headers (Content Security Policy, X-Frame-Options, etc.).
- Ensure secure handling of sensitive data (encryption at rest and in transit).
- Regularly update dependencies to patch security vulnerabilities.
- Validate and sanitize all user inputs rigorously.

## Performance Optimization Recommendations
- Optimize database queries using Django's `select_related` and `prefetch_related`.
- Implement caching strategies using Redis.
- Efficiently serve static files using Whitenoise and CDN.
- Regularly monitor and optimize Celery tasks and workers.

## Best Practices and Improvements
- Follow Django's recommended project structure and coding standards.
- Regularly audit and refactor code for maintainability.
- Write comprehensive unit and integration tests.
- Document APIs and functionalities clearly for maintainability.

## Setup Instructions
### Development Environment
```bash
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```

### Docker Deployment
```bash
docker-compose up --build
```

This documentation provides a clear overview and actionable steps to replicate and optimize the Maximum Collection Project effectively.
