from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import Lower

from home.models import Product, SellerSettlement, SellerWallet


class Command(BaseCommand):
    help = "Validate production database invariants before a release. This command never mutates data."

    def handle(self, *args, **options):
        failures = []

        duplicate_usernames = list(
            User.objects.annotate(username_key=Lower("username"))
            .values("username_key")
            .annotate(total=Count("id"))
            .filter(total__gt=1)
            .order_by("username_key")
        )
        if duplicate_usernames:
            failures.append(
                "Case-insensitive duplicate usernames: "
                + ", ".join(str(row["username_key"]) for row in duplicate_usernames)
            )

        duplicate_emails = list(
            User.objects.exclude(email="")
            .annotate(email_key=Lower("email"))
            .values("email_key")
            .annotate(total=Count("id"))
            .filter(total__gt=1)
            .order_by("email_key")
        )
        if duplicate_emails:
            failures.append(
                "Case-insensitive duplicate emails: "
                + ", ".join(str(row["email_key"]) for row in duplicate_emails)
            )

        negative_stock = Product.objects.filter(stock_quantity__lt=0).count()
        if negative_stock:
            failures.append(f"Products with negative stock quantity: {negative_stock}")

        negative_wallets = SellerWallet.objects.filter(
            pending_balance__lt=0
        ).count() + SellerWallet.objects.filter(available_balance__lt=0).count()
        if negative_wallets:
            failures.append(f"Seller wallets with negative balances: {negative_wallets}")

        inconsistent_settlements = 0
        for settlement in SellerSettlement.objects.all().only(
            "seller_gross", "platform_commission", "seller_amount"
        ):
            if settlement.seller_gross != settlement.platform_commission + settlement.seller_amount:
                inconsistent_settlements += 1
        if inconsistent_settlements:
            failures.append(
                f"Seller settlements with inconsistent amount arithmetic: {inconsistent_settlements}"
            )

        if failures:
            raise CommandError(
                "Production database preflight failed. No data was changed:\n- "
                + "\n- ".join(failures)
            )

        self.stdout.write(self.style.SUCCESS("SYSTEM PREFLIGHT: database integrity checks passed."))
