import logging
from django.core.management.base import BaseCommand
from Watchman.alerts.slackAlert import sendSlackMessage
from Watchman.models import ClientAlert, Match

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **options):
        logger.info("run_alerts #fixme")
        matches = (Match.objects
                   .filter(has_alerted=False)
                   .filter(is_fp=False)
                   .all())
        for m in matches:
            alerts = ClientAlert.objects.filter(client=m.client).filter(enabled=True).all()
            for a in alerts:
                print(f"fixme: run alert {a} on {m}")
                if a.alert_type == "slack":
                    config = a.config
                    message = f"[WATCHMAN ALERT]: Match Detected on {m.hit}"
                    sendSlackMessage(config['apikey'], config['channel'], message)
                else:
                    logger.error("Unhandled alert type: {a.alert_type}")

            m.has_alerted = True
            m.save()

