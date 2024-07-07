from django.core.management.base import BaseCommand
from Watchman.icann import czds

import sys


class Command(BaseCommand):
    def handle(self, **options):
        myicann = czds.CZDS()
        myicann.authenticate()
        links = myicann.get_zone_links()
        for l in links:
            print(l)
            data = myicann.download_one_zone(l)
            return