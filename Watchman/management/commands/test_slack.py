import logging
from django.core.management.base import BaseCommand
from Watchman.alerts.slackAlert import sendSlackMessage
from Watchman.models import ClientAlert

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **options):
        logger.info("Testing Slack Message")
        alert_list = ClientAlert.objects.filter(alert_type="slack").filter(enabled=True).all()
        for alert in alert_list:
            config = alert.config
            logger.info("Testing Slack alert %s", alert.id)
            sendSlackMessage(config['apikey'], config['channel'], "***TEST ALERT***")
