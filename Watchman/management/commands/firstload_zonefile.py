import traceback
from django.core.management.base import BaseCommand
from Watchman.icann import czds
from Watchman.models import Domain
from django.db import IntegrityError


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("zone", type=str)

    def handle(self, **options):
        myicann = czds.CZDS()
        myicann.authenticate()
        zone = options["zone"]
        link = f"https://czds-download-api.icann.org/czds/downloads/{zone}.zone"

        batch_list = []
        batch_size = 50000
        count = 0

        for domain in myicann.download_one_zone(link):
            try:
                name, tld = domain.split('.')
                d = Domain(
                    domain=domain,
                    tld=tld,
                    is_new=True,
                )
                batch_list.append(d)
                count += 1
                if count % batch_size == 0:
                    print(f"count={count}")
                    Domain.objects.bulk_create(batch_list)
                    batch_list = []

            except ValueError as e:
                #print(f"ERROR: domain={domain}")
                # traceback.print_exc()
                continue

            except IntegrityError as e:
                traceback.print_exc()
                batch_list = []

        if len(batch_list) > 0:
            try:
                Domain.objects.bulk_create(batch_list)
            except IntegrityError as e:
                traceback.print_exc()
