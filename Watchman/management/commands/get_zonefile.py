from django.conf import settings
from django.core.management.base import BaseCommand
from datetime import datetime
from Watchman.icann import czds


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("zone", type=str)

    def handle(self, **options):
        date_string = f'{datetime.now():%Y%m%d}'
        myicann = czds.CZDS()
        myicann.authenticate()
        zone = options["zone"]
        link = f"https://czds-download-api.icann.org/czds/downloads/{zone}.zone"
        filename = f"{settings.TEMP_DIR}/{date_string}-{zone}.txt"
        print(filename)
        outfile = open(filename, "w")

        for line in myicann.download_one_zone(link):
            #print(line)
            outfile.write(line)

        print("Done")