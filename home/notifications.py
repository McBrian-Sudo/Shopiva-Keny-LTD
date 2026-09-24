"""Compatibility wrapper for the canonical Shopiva notification service.

All notification creation and provider delivery is implemented in
home.notification_service. This module preserves the older call signature
used by a few payment/admin paths while routing through the single service.
"""


def _user_phone(user):
    phone = (
        getattr(user, "phone", "")
        or getattr(getattr(user, "seller_profile", None), "mpesa_phone", "")
    )
    if phone:
        return phone
    try:
        from .models import CustomerAddress
        return (
            CustomerAddress.objects.filter(user=user, is_default=True)
            .values_list("phone", flat=True)
            .first()
            or ""
        )
    except Exception:
        return ""


def notify_user(user, title, message, notification_type="system", link=""):
    if not user:
        return None
    from .notification_service import notify_user as canonical_notify_user

    return canonical_notify_user(
        user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
        email=getattr(user, "email", "") or "",
        phone=_user_phone(user),
    )
