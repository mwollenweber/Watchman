import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Watchman.settings')

app = Celery('Watchman')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(
    task_serializer='pickle',
    result_serializer='pickle',
    accept_content=['pickle']
)
app.conf.timezone = 'UTC'
app.autodiscover_tasks()


app.conf.beat_schedule = {
    # 'test': {
    #     'task': 'test',
    #     'schedule': 60.0,
    # },
    'update_zones': {
        'task': 'update_zones',
        'schedule': 3600.0,
    },
    #clean tmp


}
