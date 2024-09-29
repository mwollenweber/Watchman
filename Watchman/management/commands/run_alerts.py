import logging
from django.core.management.base import BaseCommand
from Watchman.alerts.slackAlert import sendSlackMessage
from Watchman.models import ClientAlert, Match
from Watchman.settings import BASE_URL

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **options):
        matches = (Match.objects
                   .filter(has_alerted=False)
                   .filter(is_fp=False)
                   .all())
        for m in matches:
            has_error = False
            alerts = ClientAlert.objects.filter(client=m.client).filter(enabled=True).all()
            for a in alerts:
                if a.alert_type == "slack":
                    config = a.config
                    message = f"[WATCHMAN ALERT]: Match Detected on {m.hit} for more information {BASE_URL}/alert/?id={a.id}"
                    sendSlackMessage(config['apikey'], config['channel'], message)
                elif a.alert_type == "email":
                    logger.info("fixme: alert type = email")
                elif a.alert_type == "s3":
                    logger.info("fixme: alert type = s3")
                else:
                    logger.error("Unhandled alert type: {a.alert_type}")
                    has_error = True

            if not has_error:
                m.has_alerted = True
                # fixme
                # m.save()
