from django.conf import settings
from django.core.management.base import BaseCommand
from Watchman.ct import ingest_certs


class Command(BaseCommand):
    help = "Read newly logged certificates from the Certificate Transparency logs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--max-entries",
            type=int,
            help="Newest entries to read from each log (default CT_MAX_ENTRIES_PER_LOG)",
        )
        parser.add_argument(
            "--run-for",
            type=int,
            help="Stop after this many seconds (default CT_MAX_RUN_SECONDS)",
        )
        parser.add_argument("--logs", help="Only logs whose name matches this regex")
        parser.add_argument(
            "--no-upload",
            action="store_true",
            help="Don't write the new hostnames to S3",
        )
        parser.add_argument(
            "--force", action="store_true", help="Run even if CT_ENABLED is false"
        )

    def handle(self, **options):
        if not settings.CT_ENABLED and not options["force"]:
            self.stdout.write("CT_ENABLED is false; skipping cert ingest")
            return
        stats = ingest_certs(
            max_entries=options["max_entries"],
            run_seconds=options["run_for"],
            include=options["logs"],
            upload=not options["no_upload"],
        )
        self.stdout.write(
            f"Read {stats['entries']} entries from {stats['logs']} logs: "
            f"{stats['new_names']} new hostnames, {stats['skipped']} entries skipped, "
            f"{stats['unparseable']} unparseable, {stats['errors']} log errors"
        )
