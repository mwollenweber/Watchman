from django.core.management.base import BaseCommand
from Watchman.tools import expire_new


class Command(BaseCommand):
    def handle(self, **options):
        expire_new()
