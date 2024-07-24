from django.core.management.base import BaseCommand
from Watchman.tools import run_searches

class Command(BaseCommand):
    def handle(self, **options):
        run_searches()
