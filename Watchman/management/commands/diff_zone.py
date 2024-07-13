import glob
import os
import traceback
from django.core.management.base import BaseCommand
from Watchman.tools import diff_files, getZonefiles


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("zone", type=str)

    def handle(self, **options):
        oldfile, newfile = getZonefiles(options["zone"])
        try:
            old = open(oldfile, "r")
            new = open(newfile, "r")
        except FileNotFoundError:
            traceback.print_exc()
            return

        diff = diff_files(old, new)
        for domain in diff:
            print(f"{domain}")
