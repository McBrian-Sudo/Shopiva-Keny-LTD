from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from .models import Notification


def notify_user(user, title, message, notification_type="system", link=""):
    if not user:
        return None
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
    )
    if user.email and getattr(settings, "EMAIL_NOTIFICATIONS_ENABLED", False):
        try:
            send_mail(
                subject=f"Shopiva: {title}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass
    return notification
