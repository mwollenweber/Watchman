import logging
from django.core.management.base import BaseCommand
from Watchman.icann import czds
from Watchman.models import ZoneList
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **options):
        logger.info("Initializing new zones")
        myicann = czds.CZDS()
        myicann.authenticate()
        links = myicann.get_zone_links()
        for url in links:
            try:
                zone = url.split("/")[-1].split(".")[0]
                logger.debug(f"{zone} {url}")
                ZoneList.objects.update_or_create(
                    name=zone,
                    defaults={
                        "enabled": False,
                        "status": "init",
                        "last_updated": timezone.now() - timedelta(days=365),
                        "last_completed": timezone.now() - timedelta(days=365),
                    },
                )
            except Exception as e:
                logger.error(e)
