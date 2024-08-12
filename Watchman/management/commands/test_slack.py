import logging
from django.core.management.base import BaseCommand
from Watchman.alerts.slackAlert import test

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **options):
        logger.info("meh")
        test("This is my test message")
