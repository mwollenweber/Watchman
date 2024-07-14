import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from datetime import datetime
from Watchman.icann import czds

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("zone", type=str)

    def handle(self, **options):
        count = 0
        myicann = czds.CZDS()
        myicann.authenticate()
        zone = options["zone"]
        link = f"https://czds-download-api.icann.org/czds/downloads/{zone}.zone"
        filename = f"{settings.TEMP_DIR}/{datetime.now():%Y%m%d}-{zone}.txt"
        outfile = open(filename, "w")

        for line in myicann.download_one_zone(link):
            outfile.write(f"{line}\n")
            count += 1
            if count % 10000 == 0:
                logger.debug(f"{count} domains written to {filename}")

        logger.debug("Done")
