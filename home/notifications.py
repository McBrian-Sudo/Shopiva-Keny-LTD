import json
import logging
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.mail import send_mail

from .models import Notification

logger = logging.getLogger(__name__)


def _kenya_phone(phone):
    digits = "".join(ch for ch in (phone or "") if ch.isdigit())
    if digits.startswith("254"):
        return "+" + digits
    if digits.startswith("0") and len(digits) == 10:
        return "+254" + digits[1:]
    if len(digits) == 9:
        return "+254" + digits
    return phone or ""


def _send_sms(phone, message):
    username = getattr(settings, "AFRICASTALKING_USERNAME", "")
    api_key = getattr(settings, "AFRICASTALKING_API_KEY", "")
    sender = getattr(settings, "AFRICASTALKING_SENDER_ID", "")
    if not (username and api_key and phone):
        return False
    data = urllib.parse.urlencode({
        "username": username, "to": _kenya_phone(phone),
        "message": message[:480],
        **({"from": sender} if sender else {}),
    }).encode()
    req = urllib.request.Request(
        "https://api.africastalking.com/version1/messaging",
        data=data,
        headers={"apiKey": api_key, "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            payload = json.loads(response.read().decode())
        recipients = payload.get("SMSMessageData", {}).get("Recipients", [])
        return any(r.get("status") in ("Sent", "Queued") for r in recipients)
    except Exception:
        logger.exception("Shopiva SMS delivery failed")
        return False


def _send_whatsapp(phone, message):
    token = getattr(settings, "WHATSAPP_ACCESS_TOKEN", "")
    phone_number_id = getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", "")
    if not (token and phone_number_id and phone):
        return False
    template = getattr(settings, "WHATSAPP_TEMPLATE_NAME", "")
    if template:
        body = {
            "messaging_product": "whatsapp",
            "to": _kenya_phone(phone).replace("+", ""),
            "type": "template",
            "template": {
                "name": template,
                "language": {"code": getattr(settings, "WHATSAPP_TEMPLATE_LANGUAGE", "en_US")},
                "components": [{
                    "type": "body",
                    "parameters": [{"type": "text", "text": message[:1024]}],
                }],
            },
        }
    else:
        body = {
            "messaging_product": "whatsapp",
            "to": _kenya_phone(phone).replace("+", ""),
            "type": "text",
            "text": {"preview_url": False, "body": message[:4096]},
        }
    payload = json.dumps(body).encode()
    req = urllib.request.Request(
        f"https://graph.facebook.com/{getattr(settings, 'WHATSAPP_GRAPH_VERSION', 'v23.0')}/{phone_number_id}/messages",
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode())
        return bool(result.get("messages"))
    except Exception:
        logger.exception("Shopiva WhatsApp delivery failed")
        return False


def notify_user(user, title, message, notification_type="system", link=""):
    if not user:
        return None

    notification = Notification.objects.create(
        user=user, title=title, message=message,
        notification_type=notification_type, link=link,
    )

    if user.email and getattr(settings, "EMAIL_NOTIFICATIONS_ENABLED", False):
        try:
            send_mail(
                subject=f"Shopiva: {title}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception:
            logger.exception("Shopiva email delivery failed")

    phone = (
        getattr(user, "phone", "")
        or getattr(getattr(user, "seller_profile", None), "mpesa_phone", "")
    )
    if not phone:
        try:
            from .models import CustomerAddress
            phone = CustomerAddress.objects.filter(
                user=user, is_default=True
            ).values_list("phone", flat=True).first() or ""
        except Exception:
            phone = ""
    if phone and getattr(settings, "SMS_NOTIFICATIONS_ENABLED", False):
        _send_sms(phone, f"Shopiva: {title}. {message}")
    if phone and getattr(settings, "WHATSAPP_NOTIFICATIONS_ENABLED", False):
        _send_whatsapp(phone, f"*Shopiva — {title}*\n{message}")

    return notification
