from django.core.management.base import BaseCommand
from Watchman.icann import czds


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("zone", type=str)

    def handle(self, **options):
        myicann = czds.CZDS()
        myicann.authenticate()
        myicann.load_zonefile(options["zone"])
