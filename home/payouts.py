import re

from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import SellerPayoutRequest, SellerWallet
from .notification_service import notify_user
from .payments import normalize_phone


PAYOUT_TRANSITIONS = {
    "requested": {"processing", "paid", "failed", "cancelled"},
    "processing": {"paid", "failed", "cancelled"},
    "paid": set(),
    "failed": set(),
    "cancelled": set(),
}


def normalize_payout_phone(phone):
    normalized = normalize_phone(phone)
    if not re.fullmatch(r"254[17]\d{8}", normalized):
        raise ValidationError("Enter a valid Kenyan M-PESA phone number.")
    return normalized


def request_seller_payout(seller, amount, phone, idempotency_key):
    try:
        amount = Decimal(str(amount)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError("Enter a valid payout amount.")
    if amount <= 0:
        raise ValidationError("Payout amount must be greater than zero.")
    phone = normalize_payout_phone(phone)
    idempotency_key = str(idempotency_key or "").strip()
    if not idempotency_key or len(idempotency_key) > 120:
        raise ValidationError("A valid payout request key is required.")

    try:
        with transaction.atomic():
            existing = SellerPayoutRequest.objects.filter(idempotency_key=idempotency_key).select_related("seller").first()
            if existing:
                if existing.seller_id != seller.id:
                    raise ValidationError("That payout request key is not valid for this seller.")
                return existing, False

            wallet = SellerWallet.objects.select_for_update().get(seller=seller)
            if amount > wallet.available_balance:
                raise ValidationError("The payout amount exceeds your available balance.")

            wallet.available_balance -= amount
            wallet.save(update_fields=("available_balance", "updated_at"))

            payout = SellerPayoutRequest.objects.create(
                seller=seller,
                amount=amount,
                phone=phone,
                status="requested",
                idempotency_key=idempotency_key,
            )
        return payout, True
    except IntegrityError:
        existing = SellerPayoutRequest.objects.select_related("seller").get(idempotency_key=idempotency_key)
        if existing.seller_id != seller.id:
            raise ValidationError("That payout request key is not valid for this seller.")
        return existing, False


def transition_seller_payout(
    payout_id,
    new_status,
    *,
    provider_reference=None,
    provider_response=None,
    failure_reason=None,
):
    new_status = str(new_status or "").strip().lower()
    if new_status not in {"requested", "processing", "paid", "failed", "cancelled"}:
        raise ValidationError("Invalid payout status.")

    with transaction.atomic():
        payout = SellerPayoutRequest.objects.select_for_update().select_related("seller", "seller__user").get(pk=payout_id)
        previous_status = payout.status
        if previous_status == new_status:
            return payout
        if new_status not in PAYOUT_TRANSITIONS.get(previous_status, set()):
            raise ValidationError(
                f"Payout #{payout.id} cannot move from {previous_status} to {new_status}."
            )

        wallet = SellerWallet.objects.select_for_update().get(seller=payout.seller)
        now = timezone.now()

        payout.status = new_status
        if provider_reference is not None:
            payout.provider_reference = str(provider_reference)[:120]
        if provider_response is not None:
            payout.provider_response = provider_response
        if failure_reason is not None:
            payout.failure_reason = str(failure_reason)[:255]

        if new_status == "paid":
            payout.paid_at = payout.paid_at or now
        elif new_status in {"failed", "cancelled"} and previous_status in {"requested", "processing"}:
            wallet.available_balance += payout.amount
            wallet.save(update_fields=("available_balance", "updated_at"))

        payout.save(update_fields=(
            "status",
            "provider_reference",
            "provider_response",
            "failure_reason",
            "paid_at",
            "updated_at",
        ))

        seller_user = payout.seller.user
        payout_id_value = payout.id
        amount_value = payout.amount
        if new_status == "paid":
            transaction.on_commit(
                lambda: notify_user(
                    seller_user,
                    "Seller payout confirmed",
                    f"Your Shopiva payout #{payout_id_value} for KSh {amount_value:,.2f} has been marked paid.",
                    "payout",
                    "/seller/",
                )
            )
        elif new_status in {"failed", "cancelled"}:
            transaction.on_commit(
                lambda: notify_user(
                    seller_user,
                    f"Seller payout {new_status}",
                    f"Your Shopiva payout #{payout_id_value} was marked {new_status}. The amount has been returned to your available balance.",
                    "payout",
                    "/seller/",
                )
            )
        return payout
