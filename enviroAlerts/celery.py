# Python Imports
import os

# Library/Frameworks Imports
from celery import Celery

# https://realpython.com/asynchronous-tasks-with-django-and-celery/
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enviroAlerts.settings')

app = Celery('enviroAlerts')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()