import logging
from django.core.management.base import BaseCommand
from Watchman.icann import czds
from Watchman.models import ZoneList
from Watchman.settings import BATCH_SIZE
from django.db import IntegrityError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("zone", type=str)

    def handle(self, **options):
        zone = options["zone"]
        zones = ZoneList.objects.filter(name=zone)
        for z in zones:
            logger.info(f"Disabling {z.name}")
            z.enabled = False
            z.save()
