import traceback
import re
import logging
from django.core.management.base import BaseCommand
from Watchman.tools import run_search
from Watchman.models import Domain, NewDomain, Match

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("method", type=str)

    def handle(self, **options):
        method = options["method"]
        if method == "substring":
            logging.debug("trying substring")
            match = MatchSubString("axon")
        elif method == "regex":
            logging.debug("trying regex")
            match = MatchRegEx("insomniac")
        else:
            logging.debug(f"No match for {method}")
            return

        everything = NewDomain.objects.all().values_list('domain', flat=True)
        hit_list = match.run(everything)
        for hit in hit_list:
            logging.debug(hit)
