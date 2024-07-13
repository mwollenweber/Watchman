import traceback
import re
from django.core.management.base import BaseCommand
from Watchman.tools import MatchSubString
from Watchman.models import Domain, NewDomain


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("method", type=str)

    def handle(self, **options):
        method = options["method"]
        if method == "substring":
            print("trying substring")
            match = MatchSubString("insomniac")
        else:
            print(f"No match for {method}")
            return

        everything = Domain.objects.all().values_list('domain', flat=True)
        hit_list = match.run(everything)
        for hit in hit_list:
            print(hit)
