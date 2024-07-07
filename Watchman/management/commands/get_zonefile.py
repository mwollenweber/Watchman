from django.core.management.base import BaseCommand
from Watchman.icann import czds

import sys


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("zone", type=str)


    def handle(self, **options):
        myicann = czds.CZDS()
        myicann.authenticate()
        zone = options["zone"]
        link = f"https://czds-download-api.icann.org/czds/downloads/{zone}.zone"

        for line in myicann.download_one_zone(link):
            print(line)
