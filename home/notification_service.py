import logging
import requests
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from .models import Notification, NotificationDelivery

logger = logging.getLogger(__name__)

def _delivery(notification, channel):
    return NotificationDelivery.objects.get_or_create(notification=notification, channel=channel)

def _mark(delivery, status, provider_message_id="", provider_status="", error_message=""):
    delivery.status = status
    delivery.provider_message_id = provider_message_id or ""
    delivery.provider_status = provider_status or ""
    delivery.error_message = error_message or ""
    if status == "delivered":
        delivery.delivered_at = timezone.now()
    delivery.save(update_fields=["status", "provider_message_id", "provider_status", "error_message", "delivered_at", "updated_at"])

def _send_email(delivery, recipient, title, message):
    if not settings.EMAIL_NOTIFICATIONS_ENABLED or not recipient or not settings.EMAIL_HOST_PASSWORD:
        _mark(delivery, "skipped", error_message="Email notifications are disabled or SMTP credentials are missing.")
        return
    try:
        send_mail(title, message, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)
        _mark(delivery, "delivered", provider_status="smtp accepted")
    except Exception as exc:
        logger.exception("Shopiva email notification failed")
        _mark(delivery, "failed", error_message=str(exc)[:1000])

def _send_sms(delivery, phone, message):
    if not settings.SMS_NOTIFICATIONS_ENABLED or not phone or not settings.AFRICASTALKING_API_KEY:
        _mark(delivery, "skipped", error_message="SMS notifications are disabled or Africa's Talking credentials are missing.")
        return
    try:
        response = requests.post("https://api.africastalking.com/version1/messaging", headers={"apiKey": settings.AFRICASTALKING_API_KEY, "Accept": "application/json"}, data={"username": settings.AFRICASTALKING_USERNAME, "to": phone, "message": message, **({"from": settings.AFRICASTALKING_SENDER_ID} if settings.AFRICASTALKING_SENDER_ID else {})}, timeout=15)
        response.raise_for_status()
        payload = response.json()
        recipients = (payload.get("SMSMessageData") or {}).get("Recipients") or []
        recipient = recipients[0] if recipients else {}
        _mark(delivery, "accepted", provider_message_id=str(recipient.get("messageId", "")), provider_status=str(recipient.get("status", "accepted")))
    except Exception as exc:
        logger.exception("Shopiva SMS notification failed")
        _mark(delivery, "failed", error_message=str(exc)[:1000])

def _send_whatsapp(delivery, phone, message):
    if not settings.WHATSAPP_NOTIFICATIONS_ENABLED or not phone or not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        _mark(delivery, "skipped", error_message="WhatsApp notifications are disabled or Meta credentials are missing.")
        return
    try:
        url = "https://graph.facebook.com/" + settings.WHATSAPP_GRAPH_VERSION.strip() + "/" + settings.WHATSAPP_PHONE_NUMBER_ID + "/messages"
        response = requests.post(url, headers={"Authorization": "Bearer " + settings.WHATSAPP_ACCESS_TOKEN, "Content-Type": "application/json"}, json={"messaging_product":"whatsapp","to":phone,"type":"text","text":{"preview_url":False,"body":message}}, timeout=15)
        response.raise_for_status()
        payload = response.json()
        ids = payload.get("messages") or []
        message_id = ids[0].get("id", "") if ids else ""
        _mark(delivery, "accepted", provider_message_id=message_id, provider_status="accepted")
    except Exception as exc:
        logger.exception("Shopiva WhatsApp notification failed")
        _mark(delivery, "failed", error_message=str(exc)[:1000])

def notify_user(user, notification_type, title, message, link="", email="", phone=""):
    if user is None:
        return None
    notification = Notification.objects.create(user=user, notification_type=notification_type, title=title[:160], message=message, link=link[:255])
    def dispatch():
        if email: _send_email(_delivery(notification, "email")[0], email, title, message)
        if phone:
            _send_sms(_delivery(notification, "sms")[0], phone, message)
            _send_whatsapp(_delivery(notification, "whatsapp")[0], phone, message)
    transaction.on_commit(dispatch)
    return notification