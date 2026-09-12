from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Q
from django.db.models.functions import Lower

from home.models import (
    CustomerAddress,
    DeliveryAgent,
    DeliveryLocationPing,
    Order,
    OrderItem,
    PaymentTransaction,
    Product,
    ProductReview,
    SellerPayoutRequest,
    SellerProfile,
    SellerSettlement,
    SellerWallet,
)


class Command(BaseCommand):
    help = "Validate release-critical database invariants before deployment. This command never mutates data."

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

        invalid_products = Product.objects.filter(
            Q(price__lte=0) | Q(discount_percent__lt=0) | Q(discount_percent__gt=100) | Q(stock_quantity__lt=0)
        ).count()
        if invalid_products:
            failures.append(f"Products with invalid price, discount, or stock values: {invalid_products}")

        duplicate_default_addresses = list(
            CustomerAddress.objects.filter(is_default=True)
            .values("user_id")
            .annotate(total=Count("id"))
            .filter(total__gt=1)
        )
        if duplicate_default_addresses:
            failures.append(f"Customers with multiple default addresses: {len(duplicate_default_addresses)}")

        negative_wallets = SellerWallet.objects.filter(
            Q(pending_balance__lt=0)
            | Q(available_balance__lt=0)
            | Q(total_sales__lt=0)
            | Q(total_commission__lt=0)
        ).count()
        if negative_wallets:
            failures.append(f"Seller wallets with negative balances or totals: {negative_wallets}")

        sellers_without_wallet = SellerProfile.objects.filter(is_active=True, wallet__isnull=True).count()
        if sellers_without_wallet:
            failures.append(f"Active sellers without a wallet: {sellers_without_wallet}")

        seller_rate_errors = SellerProfile.objects.exclude(commission_percent=Decimal("10.00")).count()
        if seller_rate_errors:
            failures.append(f"Seller profiles with a commission rate other than 10%: {seller_rate_errors}")

        invalid_settlements = SellerSettlement.objects.filter(
            Q(gross_amount__lt=0) | Q(platform_commission__lt=0) | Q(seller_amount__lt=0)
        ).count()
        if invalid_settlements:
            failures.append(f"Seller settlements with negative amounts: {invalid_settlements}")

        inconsistent_settlements = 0
        unpaid_settlements = 0
        for settlement in SellerSettlement.objects.all().only(
            "gross_amount", "platform_commission", "seller_amount", "order_id"
        ).select_related("order"):
            if settlement.gross_amount != settlement.platform_commission + settlement.seller_amount:
                inconsistent_settlements += 1
            if settlement.order.payment_status != "paid":
                unpaid_settlements += 1
        if inconsistent_settlements:
            failures.append(f"Seller settlements with inconsistent amount arithmetic: {inconsistent_settlements}")
        if unpaid_settlements:
            failures.append(f"Seller settlements attached to unpaid orders: {unpaid_settlements}")

        invalid_orders = Order.objects.filter(total_amount__lt=0).count()
        if invalid_orders:
            failures.append(f"Orders with negative totals: {invalid_orders}")

        invalid_items = OrderItem.objects.filter(
            Q(quantity__lte=0)
            | Q(price__lt=0)
            | Q(seller_gross__lt=0)
            | Q(platform_commission__lt=0)
            | Q(seller_net__lt=0)
        ).count()
        if invalid_items:
            failures.append(f"Order items with invalid quantity or amount values: {invalid_items}")

        inconsistent_items = 0
        for item in OrderItem.objects.all().only(
            "quantity", "price", "seller_gross", "platform_commission", "seller_net"
        ):
            line_total = item.price * item.quantity
            if item.seller_gross != line_total or item.seller_gross != item.platform_commission + item.seller_net:
                inconsistent_items += 1
        if inconsistent_items:
            failures.append(f"Order items with inconsistent financial arithmetic: {inconsistent_items}")

        inconsistent_order_totals = 0
        for order in Order.objects.all().only("id", "total_amount"):
            item_total = sum(
                (item.price * item.quantity for item in order.items.all()),
                Decimal("0.00"),
            )
            if order.total_amount != item_total:
                inconsistent_order_totals += 1
        if inconsistent_order_totals:
            failures.append(f"Orders whose totals do not equal their line items: {inconsistent_order_totals}")

        invalid_reviews = ProductReview.objects.filter(Q(rating__lt=1) | Q(rating__gt=5)).count()
        if invalid_reviews:
            failures.append(f"Product reviews with ratings outside 1-5: {invalid_reviews}")

        invalid_payments = PaymentTransaction.objects.filter(amount__lte=0).count()
        if invalid_payments:
            failures.append(f"Payment transactions with non-positive amounts: {invalid_payments}")

        for payment in PaymentTransaction.objects.filter(method="mpesa", status="paid").only(
            "id", "provider_reference", "paid_at", "order_id", "amount", "phone"
        ):
            if not payment.provider_reference or not payment.paid_at:
                failures.append(f"M-PESA payment #{payment.id} is marked paid without provider reference/time.")

        inconsistent_paid_orders = Order.objects.filter(payment_status="paid").exclude(status="cancelled").filter(
            paid_at__isnull=True
        ).count()
        if inconsistent_paid_orders:
            failures.append(f"Paid orders missing paid_at: {inconsistent_paid_orders}")

        invalid_payouts = SellerPayoutRequest.objects.filter(amount__lte=0).count()
        if invalid_payouts:
            failures.append(f"Seller payout requests with non-positive amounts: {invalid_payouts}")

        for agent in DeliveryAgent.objects.exclude(current_latitude__isnull=True).only(
            "id", "current_latitude", "current_longitude"
        ):
            if agent.current_longitude is None or not (-90 <= float(agent.current_latitude) <= 90) or not (-180 <= float(agent.current_longitude) <= 180):
                failures.append(f"Delivery agent #{agent.id} has invalid live coordinates.")
        invalid_pings = 0
        for ping in DeliveryLocationPing.objects.only(
            "id", "latitude", "longitude", "accuracy_meters", "speed_mps"
        ):
            if not (-90 <= float(ping.latitude) <= 90) or not (-180 <= float(ping.longitude) <= 180):
                invalid_pings += 1
                continue
            if ping.accuracy_meters is not None and ping.accuracy_meters < 0:
                invalid_pings += 1
            if ping.speed_mps is not None and ping.speed_mps < 0:
                invalid_pings += 1
        if invalid_pings:
            failures.append(f"Delivery location samples with invalid coordinates/measurements: {invalid_pings}")

        if failures:
            raise CommandError(
                "Production database preflight failed. No data was changed:\n- " + "\n- ".join(failures)
            )

        self.stdout.write(self.style.SUCCESS("SYSTEM PREFLIGHT: all release-critical database integrity checks passed."))
