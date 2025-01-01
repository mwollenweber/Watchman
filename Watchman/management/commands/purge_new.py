from django.core.management.base import BaseCommand
from Watchman.tools import purge_new


class Command(BaseCommand):
    def handle(self, **options):
        purge_new()
