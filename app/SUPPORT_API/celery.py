import os
from celery import Celery

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SUPPORT_API.settings')

# app = Celery('app')
app = Celery('SUPPORT_API')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
