import os
from pathlib import Path
from urllib.parse import urlparse
from datetime import timedelta

from django.core.management.utils import get_random_secret_key
# from decouple import config, Csv, AutoConfig
import dj_database_url

DEBUG=False
BASE_DIR = Path(__file__).resolve().parent.parent

# config = AutoConfig(search_path='/home/tax-latest/.env')

SECRET_KEY = os.environ.get('SECRET_KEY', default=get_random_secret_key())

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "134.209.187.156", "lasimra.maxvaafrica.com", "flower.maxvaafrica.com"]
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_celery_beat',
    'django_celery_results',
    # 'django_tables2',
    # 'django_filters',
    'template_partials',
    'import_export',
    'django_htmx',
    'easyaudit',
    'simple_history',
    'anymail',
    'account',
    'tax',
    'agency',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'corsheaders.middleware.CorsMiddleware',  # If CORS enabled
    'django.middleware.common.CommonMiddleware',
    'agency.middleware.AgencyAreaMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'easyaudit.middleware.easyaudit.EasyAuditMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'core.middleware.CheckProfileMiddleware',
]

ROOT_URLCONF = 'core.urls'

default_loaders = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]
cached_loaders = [("django.template.loaders.cached.Loader", default_loaders)]
partial_loaders = [("template_partials.loader.Loader", cached_loaders)]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [BASE_DIR / 'templates'],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "debug": DEBUG,
            "loaders": partial_loaders,
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql', # django.db.backends.postgresql
        'NAME': os.environ.get("DB_NAME"),
        'USER': os.environ.get("DB_USER"),
        'PASSWORD': os.environ.get("DB_PASS"),
        'HOST': os.environ.get("DB_HOST"),
        'PORT': os.environ.get("DB_PORT", "5432"),
        'OPTIONS': {
            'connect_timeout': 5,
            # Explicitly disable socket connection
            'client_encoding': 'UTF8',
            'sslmode': 'require' if os.environ.get('DB_SSL') == 'True' else 'prefer'
        },
    }
}
# print("Database connected successfully")
# HTTPS / Security
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True


# else:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / 'db.sqlite3',
#         }
#     }

    
    


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/opt/tax-latest/static/'
STATIC_ROOT = BASE_DIR / "opt/tax-latest/staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/opt/tax-latest/assets/media/"
MEDIA_ROOT = BASE_DIR / "opt/tax-latest/assets/media"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "account.User"

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True

# Login settings
LOGIN_URL = "/clients/"
LOGIN_REDIRECT_URL = "/clients/dashboard/"

# Email (Brevo)
EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
DEFAULT_FROM_EMAIL = "LASIMRA <no-reply@maximumcollections.com>"
EMAIL_HOST_USER = "LASIMRA <no-reply@maximumcollections.com>"

ANYMAIL = {
    "BREVO_API_KEY": os.environ.get('BREVO_API_KEY'),
    # "BREVO_API_KEY": config('BREVO_API_KEY'),
    "BREVO_API_URL": "https://api.brevo.com/v3/",
}

# Paystack
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')

# Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_REDIS_URL', default='redis://redis:6379')
CELERY_RESULT_BACKEND = "django-db"
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
CELERY_TIMEZONE = "Africa/Lagos"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
os.environ["CELERY_STORE_ERRORS_EVEN_IF_IGNORED"] = "True"

# CORS (if needed)
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", default="")

# Cache (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_CACHE_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Optional logging for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO' if not DEBUG else 'DEBUG',
    },
}

# Sentry (optional)
# import sentry_sdk
# sentry_sdk.init(
#     dsn=os.environ.get("SENTRY_KEY"),
#     send_default_pii=True,
# )

# Fixture paths
FIXTURE_DIRS = ['account/features', 'tax/features', 'agency/features', 'features']

# Misc
IMPORT_EXPORT_USE_TRANSACTIONS = True
TAX_AUTHOURITY_EMAIL = os.environ.get("TAX_AUTHOURITY_EMAIL")
# Django Commands
DJANGO_SETTINGS_MODULE='core.settings'
