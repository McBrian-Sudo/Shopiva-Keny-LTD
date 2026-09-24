from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from home.models import DeliveryLocationPing


class Command(BaseCommand):
    help = "Remove delivery GPS history older than the configured retention window."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=90,
            help="Delete pings older than this many days (default: 90).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report the number of records without deleting them.",
        )

    def handle(self, *args, **options):
        days = max(1, min(options["days"], 3650))
        cutoff = timezone.now() - timedelta(days=days)
        queryset = DeliveryLocationPing.objects.filter(recorded_at__lt=cutoff)
        count = queryset.count()
        if options["dry_run"]:
            self.stdout.write(
                f"Delivery location retention dry run: {count} pings older than {days} days."
            )
            return
        deleted, _ = queryset.delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"Delivery location retention complete: deleted {deleted} records older than {days} days."
            )
        )
