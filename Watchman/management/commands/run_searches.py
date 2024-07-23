import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from Watchman.models import Search, NewDomain, Domain, Match
from Watchman.tools import run_search
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **options):
        logging.info("Running Searches")

        #run the new domain as target list first
        logger.info("Running newdomain searches")
        target_list = NewDomain.objects.all().values_list('domain', flat=True)
        search_list = Search.objects.filter(is_active=True, database='newdomains')
        for s in search_list:
            if s.last_completed < timezone.now() - timedelta(seconds=s.update_interval):
                if s.last_updated < timezone.now() - timedelta(seconds=settings.MIN_UPDATE_INTERVAL):
                    logger.info(f"{s} on {len(target_list)} domains")
                    #todo = update status timestamps
                    hits = run_search(s.method, s.criteria, target_list, tolerance=s.tolerance) or []
                    for h in hits:
                        print(f"hit={h}")

        #run searches on all domains a
        logger.info("Running full domain searches")
        target_list = Domain.objects.all().values_list('domain', flat=True)
        search_list = Search.objects.filter(is_active=True, database='domains')
        for s in search_list:
            if s.last_completed < timezone.now() - timedelta(seconds=s.update_interval):
                if s.last_updated < timezone.now() - timedelta(seconds=settings.MIN_UPDATE_INTERVAL):
                    logger.info(f"{s} on {len(target_list)} domains")
                    # todo = update status timestamps
                    hits = run_search(s.method, s.criteria, target_list, tolerance=s.tolerance) or []
                    for h in hits:
                        print(f"hit={h}")

