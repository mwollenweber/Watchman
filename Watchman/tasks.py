from celery.utils.log import get_task_logger
from django.conf import settings
from Watchman.models import ZoneList
from django.utils import timezone
from datetime import timedelta
from Watchman.icann.czds import update_zonefile
from Watchman.tools import (
    diff_files,
    getZonefiles,
    load_diff,
    run_searches,
    expire_new,
    clean_temp,
)
from .celery import app

logger = get_task_logger(__name__)


@app.task(name="run_matches")
def run_matches():
    run_searches()


@app.task(name="clean_tmp")
def clean_tmp_task():
    clean_temp()


@app.task(name="expire_new")
def expire_new_task():
    expire_new()


@app.task(name="test")
def test():
    logger.info("Celery is sending tasks!!!")


@app.task(name="diff_zone")
def diff_zone(zone):
    logger.info(f"diffing zone {zone}")
    try:
        zone.status = "diffing"
        zone.last_updated = timezone.now()
        zone.save()

        oldfile, newfile = getZonefiles(zone.name)
        old = open(oldfile, "r")
        new = open(newfile, "r")
        domain_list = diff_files(old, new)
        load_diff(domain_list)

        zone.status = "good"
        now = timezone.now()
        zone.last_updated = now
        zone.last_completed = now
        zone.last_diffed = now
        zone.save()
        logger.info(f"DONE zone={zone.name}")

    except FileNotFoundError as e:
        logger.error(e)
        zone.last_error = timezone.now()
        zone.error_message = f"{e}"
        zone.status = "error"
        zone.save()
        return

    except Exception as e:
        logger.error(e)
        zone.last_error = timezone.now()
        zone.error_message = f"{e}"
        zone.status = "error"
        zone.save()


@app.task(name="update_zone")
def update_zone(zone):
    logger.info(f"updating zone={zone.name}")
    try:
        zone.status = "updating"
        zone.last_updated = timezone.now()
        zone.save()

        update_zonefile(zone)

        zone.status = "needs_diff"
        now = timezone.now()
        zone.last_updated = now
        zone.save()

        diff_zone.apply_async(args=[zone])
        logger.info(f"DONE zone={zone.name}")

    except Exception as e:
        logger.error(e)
        zone.last_error = timezone.now()
        zone.error_message = f"{e}"
        zone.status = "error"
        zone.save()


@app.task(name="update_zones")
def update_zones():
    logger.info("Checking zones updates...")
    healthy_zones = ZoneList.objects.filter(
        enabled=True,
        # status='good',
    )

    for zone in healthy_zones:
        try:
            if zone.last_completed < timezone.now() - timedelta(
                seconds=zone.update_interval
            ):
                if zone.last_updated < timezone.now() - timedelta(
                    seconds=settings.MIN_ZONE_TIME
                ):
                    logger.info(f"Enqueing {zone.name}")
                    update_zone.apply_async(args=[zone])

        except Exception as e:
            logger.error(e)
            zone.last_error = timezone.now()
            zone.error_message = f"{e}"
            zone.status = "error"
            zone.save()
