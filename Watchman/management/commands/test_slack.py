import logging
from django.core.management.base import BaseCommand
from Watchman.alerts.slackAlert import sendSlackMessage
from Watchman.models import SlackConfig

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **options):
        logger.info("Testing Slack Message")
        config_list = SlackConfig.objects.all()
        for config in config_list:
            logger.info("Testing Slack Config %s", config.id)
            sendSlackMessage(config.api_key, config.channel, "***TEST ALERT***")
