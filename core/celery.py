import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
# this is also used in manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
# app = Celery('core',
#                broker='redis://localhost:6379/0',
#                backend='redis://localhost:6379/0')

# app.conf.broker_url = 'redis://localhost:6379/0'

app.conf.enable_utc = False
app.conf.update(timezone="Africa/Lagos")

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


app.conf.beat_scheduler = {
    'send_annual_tax_emails_to_clients': {
        'task':'agency.tasks.send_annual_tax_emails_to_clients',
        'schedule': crontab(hour=12, minute=1),
    }
}
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
# app.autodiscover_tasks(['agency'])

# We used CELERY_BROKER_URL in settings.py instead of:
# app.conf.broker_url = ''

# We used CELERY_BEAT_SCHEDULER in settings.py instead of:
# app.conf.beat_scheduler = ''django_celery_beat.schedulers.DatabaseScheduler'

#######################################
# RUN CELERY: celery -A core worker --beat
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# CELERY COMMANDS
# celery -A core worker -l INFO                     # WORKER
# celery -A core beat -l INFO                       # BEAT SCHEDULER