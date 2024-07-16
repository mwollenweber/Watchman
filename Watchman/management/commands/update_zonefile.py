import logging
from django.core.management.base import BaseCommand
from Watchman.icann.czds import update_zonefile


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("zone", type=str)

    def handle(self, **options):
        zone = options["zone"]
        update_zonefile(zone)
