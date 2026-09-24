from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from home.models import Order, PaymentTransaction
from home.payments import _release_reserved_inventory, query_mpesa_stk


TERMINAL_FAILURE_CODES = {
    "1", "17", "1001", "1019", "1025", "1032",
    "1037", "2001", "2002", "2028", "2029",
}


class Command(BaseCommand):
    help = "Reconcile stale M-PESA payment requests with the Daraja STK Query API."

    def add_arguments(self, parser):
        parser.add_argument(
            "--age-minutes",
            type=int,
            default=10,
            help="Only reconcile payments older than this many minutes.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Maximum number of stale payments to inspect.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Query payments and report terminal results without changing records.",
        )

    def handle(self, *args, **options):
        age_minutes = max(1, options["age_minutes"])
        limit = max(1, min(options["limit"], 1000))
        cutoff = timezone.now() - timedelta(minutes=age_minutes)
        payments = list(
            PaymentTransaction.objects.filter(
                method="mpesa",
                status__in={"initiated", "pending"},
                created_at__lte=cutoff,
            )
            .exclude(checkout_request_id="")
            .order_by("created_at")[:limit]
        )

        checked = failed = pending = errors = 0
        for payment in payments:
            checked += 1
            try:
                provider = query_mpesa_stk(payment)
            except Exception as exc:
                errors += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"M-PESA payment #{payment.id}: provider query unavailable; left pending ({str(exc)[:180]})"
                    )
                )
                continue

            result_code = str(provider.get("ResultCode", "")).strip()
            if result_code == "0":
                pending += 1
                self.stdout.write(
                    f"M-PESA payment #{payment.id}: provider accepted the STK request; waiting for callback receipt validation."
                )
                with transaction.atomic():
                    current = PaymentTransaction.objects.select_for_update().get(pk=payment.pk)
                    current.raw_response = {
                        **(current.raw_response or {}),
                        "last_stk_query": provider,
                        "reconciled_at": timezone.now().isoformat(),
                    }
                    current.status = "pending"
                    current.save(update_fields=("status", "raw_response", "updated_at"))
                continue

            if result_code not in TERMINAL_FAILURE_CODES:
                pending += 1
                continue

            if options["dry_run"]:
                failed += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"M-PESA payment #{payment.id}: terminal provider result {result_code}; dry run, no records changed."
                    )
                )
                continue

            with transaction.atomic():
                current = PaymentTransaction.objects.select_for_update().get(pk=payment.pk)
                order = Order.objects.select_for_update().get(pk=current.order_id)
                current.status = "failed"
                current.raw_response = {
                    **(current.raw_response or {}),
                    "last_stk_query": provider,
                    "reconciled_at": timezone.now().isoformat(),
                }
                if not current.inventory_released:
                    _release_reserved_inventory(order)
                    current.inventory_released = True
                order.payment_status = "failed"
                order.save(update_fields=("payment_status",))
                current.save(
                    update_fields=("status", "raw_response", "inventory_released", "updated_at")
                )
            failed += 1
            self.stdout.write(
                self.style.WARNING(
                    f"M-PESA payment #{payment.id}: terminal provider failure {result_code}; order #{payment.order_id} marked failed and inventory released."
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"M-PESA reconciliation complete: checked={checked}, failed={failed}, pending={pending}, errors={errors}."
            )
        )
