import glob
import os
import logging
from django.core.management.base import BaseCommand
from Watchman.settings import TEMP_DIR, MAX_TEMP_AGE
from time import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **options):
        files = glob.glob(f"{TEMP_DIR}/*txt")
        current_time = time()

        for f in files:
            time_delta_days = (current_time - os.path.getmtime(f)) / (60 * 60 * 24)
            if time_delta_days > MAX_TEMP_AGE:
                logger.info(f"deleting: {f}")
                os.remove(f)
