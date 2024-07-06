import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyGymCheckin.settings')

app = Celery('EasyGymCheckin')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.timezone = 'UTC'
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'test': {
        'task': 'test',
        'schedule': 60.0,
    },
}
