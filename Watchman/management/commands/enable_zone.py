import logging
from django.core.management.base import BaseCommand
from Watchman.icann import czds
from Watchman.models import ZoneList
from Watchman.settings import BATCH_SIZE
from django.db import IntegrityError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("zone", nargs="+")

    def handle(self, **options):
        zonename_list = options["zone"]
        for zonename in zonename_list:
            zones = ZoneList.objects.filter(name=zonename)
            for z in zones:
                logger.info(f"Enabling {z.name}")
                z.enabled = True
                z.save()
