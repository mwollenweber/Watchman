import logging
from django.core.management.base import BaseCommand
from Watchman.tools import run_alerts

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **options):
        run_alerts()
