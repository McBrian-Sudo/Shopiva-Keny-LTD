from django.db.models.signals import post_save
from django.dispatch import receiver

from home.models import Order

from .models import SupportTicket


AUTO_TICKET_STATUSES = {"cancelled"}
AUTO_TICKET_PAYMENT_STATUSES = {"failed"}


def _ensure_ticket(*, user, role, subject, category, priority, order):
    if not user:
        return None
    existing = SupportTicket.objects.filter(
        user=user,
        role=role,
        order_reference=order.tracking_code or str(order.id),
        status__in=("open", "in_progress", "waiting_for_customer"),
        subject=subject,
    ).first()
    if existing:
        return existing
    return SupportTicket.objects.create(
        user=user,
        role=role,
        subject=subject[:160],
        category=category[:80],
        priority=priority,
        status="open",
        order_reference=order.tracking_code or str(order.id),
    )


@receiver(post_save, sender=Order)
def create_automatic_support_cases(sender, instance, created, **kwargs):
    """Create actionable support cases when the system detects a failed payment or cancellation."""
    if not instance.customer:
        return

    if instance.payment_status in AUTO_TICKET_PAYMENT_STATUSES:
        ticket = _ensure_ticket(
            user=instance.customer,
            role="customer",
            subject=f"Payment assistance for order {instance.tracking_code or instance.id}",
            category="Payment & M-PESA",
            priority="urgent",
            order=instance,
        )
        if ticket and not ticket.messages.exists():
            from .models import SupportMessage
            SupportMessage.objects.create(
                ticket=ticket,
                author=None,
                body="Shopiva detected a payment failure for this order and opened this case automatically. Please review the payment status and reply here if you need assistance.",
                from_staff=True,
            )

    if instance.status in AUTO_TICKET_STATUSES:
        ticket = _ensure_ticket(
            user=instance.customer,
            role="customer",
            subject=f"Order cancellation assistance · {instance.tracking_code or instance.id}",
            category="Orders",
            priority="high",
            order=instance,
        )
        if ticket and not ticket.messages.exists():
            from .models import SupportMessage
            SupportMessage.objects.create(
                ticket=ticket,
                author=None,
                body="Shopiva detected that this order was cancelled and opened a support case automatically so the order outcome can be reviewed.",
                from_staff=True,
            )

        # A cancellation can also affect sellers. Give each affected seller their own private case.
        for item in instance.items.select_related("seller__user").all():
            seller = getattr(item.seller, "user", None)
            if not seller:
                continue
            ticket = _ensure_ticket(
                user=seller,
                role="seller",
                subject=f"Cancelled order assistance · {instance.tracking_code or instance.id}",
                category="Seller Store",
                priority="high",
                order=instance,
            )
            if ticket and not ticket.messages.exists():
                from .models import SupportMessage
                SupportMessage.objects.create(
                    ticket=ticket,
                    author=None,
                    body="Shopiva detected a cancellation affecting one of your sales and opened this support case automatically. Review the case for assistance.",
                    from_staff=True,
                )
