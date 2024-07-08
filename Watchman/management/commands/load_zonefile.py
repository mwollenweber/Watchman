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

        for domain in myicann.download_one_zone(link):
            try:
                name, tld = domain.split('.')
                # obj, created = Domain.objects.update_or_create(
                #     domain=domain,
                #     tld=tld,
                # )
                d = Domain.objects.create(
                    name=domain,
                    tld=tld,
                    is_new=True,
                )
                #d.save()

            except ValueError as e:
                print(f"ERROR: domain={domain}")
                # traceback.print_exc()

            except IntegrityError as e:
                #domain already existed -- don't care
                continue
