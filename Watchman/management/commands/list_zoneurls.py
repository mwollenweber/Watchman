import logging
from django.core.management.base import BaseCommand
from Watchman.icann import czds

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, **options):
        myicann = czds.CZDS()
        myicann.authenticate()
        links = myicann.get_zone_links()
        for l in links:
            logger.debug(l)
            # data = myicann.download_one_zone(l)
