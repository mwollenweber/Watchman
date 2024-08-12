import logging
from django.utils import timezone
from datetime import timedelta
from django.core.management.base import BaseCommand
from Watchman.icann.czds import update_zonefile
from Watchman.models import ZoneList
from Watchman.tools import diff_zone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("zone", nargs="+")

    def handle(self, **options):
        zone_list = options["zone"]
        for zonename in zone_list:
            try:
                logger.info(f"Trying to update zone={zonename}")
                zone = ZoneList.objects.filter(name=f"{zonename}").first()
                logger.info(f"Got Zone={zone.name}")

                zone.status = "updating"
                zone.last_updated = timezone.now()
                zone.save()

                update_zonefile(zone)

                zone.status = "needs_diff"
                now = timezone.now()
                zone.last_updated = now
                zone.save()

                diff_zone(zone)
                logger.info(f"DONE zone={zone.name}")

            except Exception as e:
                logger.error(e)
                if zone:
                    zone.last_error = timezone.now()
                    zone.error_message = f"{e}"
                    zone.status = "error"
                    zone.save()
