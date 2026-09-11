import json
import logging
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Notification, NotificationDelivery

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
        return {"status": "skipped", "error": "SMS provider credentials or phone number missing"}

    data = urllib.parse.urlencode({
        "username": username,
        "to": _kenya_phone(phone),
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
        recipient = recipients[0] if recipients else {}
        status = str(recipient.get("status", "")).lower()
        if status in {"success", "sent", "queued"}:
            return {
                "status": "accepted",
                "provider_message_id": recipient.get("messageId", ""),
                "provider_status": recipient.get("status", ""),
            }
        return {
            "status": "failed",
            "provider_status": recipient.get("status", ""),
            "error": recipient.get("statusCode") or payload.get("SMSMessageData", {}).get("Message", "SMS provider rejected the message"),
        }
    except Exception as exc:
        logger.exception("Shopiva SMS delivery failed")
        return {"status": "failed", "error": str(exc)[:1000]}


def _send_whatsapp(phone, message):
    token = getattr(settings, "WHATSAPP_ACCESS_TOKEN", "")
    phone_number_id = getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", "")
    if not (token and phone_number_id and phone):
        return {"status": "skipped", "error": "WhatsApp provider credentials or phone number missing"}

    template = getattr(settings, "WHATSAPP_TEMPLATE_NAME", "")
    if not template:
        return {
            "status": "skipped",
            "error": "Approved WhatsApp template is not configured",
        }

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
        messages = result.get("messages", [])
        if messages:
            return {
                "status": "accepted",
                "provider_message_id": messages[0].get("id", ""),
                "provider_status": "accepted",
            }
        return {"status": "failed", "error": "WhatsApp provider returned no message ID"}
    except Exception as exc:
        logger.exception("Shopiva WhatsApp delivery failed")
        return {"status": "failed", "error": str(exc)[:1000]}


def _record_delivery(notification, channel, result):
    delivery, _ = NotificationDelivery.objects.update_or_create(
        notification=notification,
        channel=channel,
        defaults={
            "status": result.get("status", "failed"),
            "provider_message_id": result.get("provider_message_id", "")[:255],
            "provider_status": str(result.get("provider_status", ""))[:100],
            "error_message": str(result.get("error", ""))[:5000],
        },
    )
    return delivery


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
        delivery = NotificationDelivery.objects.create(
            notification=notification, channel="email", status="pending"
        )
        try:
            sent = send_mail(
                subject=f"Shopiva: {title}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            delivery.status = "accepted" if sent else "failed"
            delivery.provider_status = "accepted" if sent else "rejected"
            if not sent:
                delivery.error_message = "SMTP provider accepted no recipients"
            delivery.save()
        except Exception as exc:
            delivery.status = "failed"
            delivery.error_message = str(exc)[:5000]
            delivery.save()
            logger.exception("Shopiva email delivery failed")
    elif user.email:
        _record_delivery(
            notification, "email",
            {"status": "skipped", "error": "Email notifications are disabled"},
        )

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

    if getattr(settings, "SMS_NOTIFICATIONS_ENABLED", False):
        _record_delivery(
            notification, "sms",
            _send_sms(phone, f"Shopiva: {title}. {message}") if phone
            else {"status": "skipped", "error": "No phone number available"},
        )

    if getattr(settings, "WHATSAPP_NOTIFICATIONS_ENABLED", False):
        _record_delivery(
            notification, "whatsapp",
            _send_whatsapp(phone, f"Shopiva — {title}\n{message}") if phone
            else {"status": "skipped", "error": "No phone number available"},
        )

    return notification
