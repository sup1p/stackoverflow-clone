import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StackOverflowCopy.settings')

# creating celery project with project name
app = Celery('StackOverflowCopy')

# we use namespace CELERY to get config from setting of the app
app.config_from_object('django.conf:settings', namespace='CELERY')

# automatically find tasks in django app
app.autodiscover_tasks()