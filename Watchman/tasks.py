from celery.utils.log import get_task_logger
from django.conf import settings
from Watchman.models import ZoneList
from django.utils import timezone
from datetime import timedelta
from Watchman.icann.czds import update_zonefile
from .celery import app


logger = get_task_logger(__name__)


@app.task(name="test")
def test():
    logger.info("Celery is sending tasks!!!")


@app.task(name="update_zone")
def update_zone(zone):
    logger.info(f"updating zone={zone.name}")
    try:
        zone.status = "working"
        zone.last_updated = timezone.now()
        zone.save()

        update_zonefile(zone)

        zone.status = "good"
        now = timezone.now()
        zone.last_updated = now
        zone.last_completed = now
        zone.save()
        logger.info(f"DONE zone={zone.name}")

    except Exception as e:
        logger.error(e)
        zone.last_updated = timezone.now()
        zone.status = "error"
        zone.save()


@app.task(name="update_zones")
def update_zones():
    logger.info("Checking zones updates...")
    healthy_zones = ZoneList.objects.filter(
        enabled=True,
        #status='good',
    )

    for zone in healthy_zones:
        if zone.last_completed < timezone.now() - timedelta(seconds=zone.update_interval):
            if zone.last_updated < timezone.now() - timedelta(seconds=settings.MIN_ZONE_TIME):
                logger.info(f"Enqueing {zone.name}")
                update_zone.apply_async(args=[zone])
