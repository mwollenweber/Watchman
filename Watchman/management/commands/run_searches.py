import logging
from django.core.management.base import BaseCommand
from Watchman.tools import diff_files, getZonefiles, load_diff

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **options):
        logging.debug("Running Searches")
