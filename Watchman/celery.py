import os
from celery import Celery
from django.conf import settings

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
    'update_zones': {
        'task': 'update_zones',
        'schedule': settings.ZONE_UPDATE_INTERVAL,
    },
    'run_matches': {
        'task': 'run_matches',
        'schedule': settings.MATCH_UPDATE_INTERVAL,
    },
    'expire_new': {
        'task': 'expire_new',
        'schedule': 3600,
    },

    #clean tmp folder

    #clean NewDomains

    #clean matches

    #run Watch

}
