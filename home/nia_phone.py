import json
import os
import re
from urllib.parse import urlencode

from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import CustomerAddress, DeliveryAgent, NiaCallSession, Order, OrderItem, Product


KENYA_PHONE_RE = re.compile(r"^254[17]\d{8}$")


def _env(name, default=""):
    return os.getenv(name, default).strip()


def _public_site_url(request):
    configured = _env("PUBLIC_SITE_URL")
    return (configured or request.build_absolute_uri("/").rstrip("/")).rstrip("/")


def _normalize_phone(value):
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    if digits.startswith("254"):
        normalized = digits
    elif digits.startswith("0"):
        normalized = "254" + digits[1:]
    elif digits.startswith("7") or digits.startswith("1"):
        normalized = "254" + digits
    else:
        normalized = digits
    return normalized


def _caller_phone(request):
    if not request.user.is_authenticated:
        return ""
    seller = getattr(request.user, "seller_profile", None)
    if seller and seller.is_active:
        return _normalize_phone(seller.mpesa_phone)

    address = (
        CustomerAddress.objects.filter(user=request.user, is_default=True)
        .values_list("phone", flat=True)
        .first()
    )
    if address:
        return _normalize_phone(address)

    latest = (
        Order.objects.filter(email__iexact=request.user.email)
        .exclude(phone="")
        .order_by("-created_at")
        .values_list("phone", flat=True)
        .first()
    )
    return _normalize_phone(latest)


def _role_for(request):
    if request.user.is_staff or request.user.is_superuser:
        return NiaCallSession.ROLE_ADMIN
    seller = getattr(request.user, "seller_profile", None)
    if seller and seller.is_active:
        return NiaCallSession.ROLE_SELLER
    return NiaCallSession.ROLE_CUSTOMER


def _role_context(request, role):
    if role == NiaCallSession.ROLE_ADMIN:
        recent_orders = list(
            Order.objects.order_by("-created_at")
            .values("id", "tracking_code", "status", "payment_status", "total_amount")[:15]
        )
        return {
            "role_name": "Admin Operations Copilot",
            "summary": {
                "products": Product.objects.count(),
                "pending_orders": Order.objects.filter(status="pending").count(),
                "paid_orders": Order.objects.filter(payment_status="paid").count(),
                "failed_mpesa": Order.objects.filter(payment_status="failed").count(),
                "active_riders": DeliveryAgent.objects.filter(
                    is_active=True, status__in=("available", "on_delivery")
                ).count(),
                "staff_pending": DeliveryAgent.objects.filter(is_active=False).count(),
                "recent_orders": recent_orders,
            },
        }

    seller = getattr(request.user, "seller_profile", None)
    if role == NiaCallSession.ROLE_SELLER and seller:
        products = list(
            Product.objects.filter(seller=seller, is_active=True)
            .values("id", "name", "category", "price", "discount_percent", "stock_quantity")[:40]
        )
        orders = list(
            Order.objects.filter(items__seller=seller).distinct()
            .order_by("-created_at")
            .values("id", "tracking_code", "status", "payment_status", "total_amount")[:20]
        )
        wallet = getattr(seller, "wallet", None)
        return {
            "role_name": "Seller Copilot",
            "summary": {
                "products": products,
                "orders": orders,
                "pending_balance": str(wallet.pending_balance) if wallet else "0.00",
                "available_balance": str(wallet.available_balance) if wallet else "0.00",
                "total_sales": str(wallet.total_sales) if wallet else "0.00",
            },
        }

    orders = list(
        Order.objects.filter(email__iexact=request.user.email)
        .order_by("-created_at")
        .values("id", "tracking_code", "status", "payment_status", "total_amount")[:10]
    )
    cart = request.session.get("cart", {})
    cart_rows = []
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id), is_active=True)
            cart_rows.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "quantity": int(quantity),
                    "price": str(product.discounted_price),
                }
            )
        except (Product.DoesNotExist, TypeError, ValueError):
            continue
    return {
        "role_name": "Shopping Copilot",
        "summary": {"recent_orders": orders, "cart": cart_rows},
    }


def _opening_text(context):
    role = context["role_name"]
    if role == "Admin Operations Copilot":
        return (
            "Hi. This is Nia, your Shopiva Operations Copilot. "
            "I can brief you on orders, payments, delivery, staff approvals and stock. "
            "What would you like me to check?"
        )
    if role == "Seller Copilot":
        return (
            "Hi. This is Nia, your Shopiva Seller Copilot. "
            "I can help with your stock, orders, sales and payout balance. "
            "What would you like me to check?"
        )
    return (
        "Hi. This is Nia, your Shopiva Shopping Copilot. "
        "I can help with your Shopiva orders and shopping. What can I help you with?"
    )


def _ai_reply(session, user_text):
    api_key = _env("OPENAI_API_KEY")
    if not api_key:
        return "I'm unable to use the full Nia intelligence service right now, but your call is connected. Please use the Shopiva dashboard for live information."

    context = _role_context(type("Request", (), {"user": session.user})(), session.role)
    history = session.conversation[-12:]
    prompt = f"""
You are Nia, the phone assistant for Shopiva Kenya.
This is a live phone conversation with an authenticated Shopiva user.
Role: {context["role_name"]}.
Use only the supplied Shopiva data. Never invent prices, order status, stock, payments, delivery status, balances or approvals.
Keep spoken answers concise and natural, generally under 70 words.
For M-PESA, only an exact status of paid means paid.
Do not claim to send emails, access banks, sign contracts, change records, approve staff, initiate payouts or make external purchases.
Those capabilities are not enabled in this phone channel yet.
SHOPIVA CONTEXT:
{json.dumps(context["summary"], default=str, ensure_ascii=False)}
RECENT CONVERSATION:
{json.dumps(history, default=str, ensure_ascii=False)}
USER:
{user_text}
"""
    try:
        from openai import OpenAI

        response = OpenAI(api_key=api_key).responses.create(
            model=_env("OPENAI_MODEL", "gpt-5.6-luna"),
            input=prompt,
        )
        return (response.output_text or "").strip() or "I did not get enough information to answer that."
    except Exception:
        return "Nia is temporarily unable to reach the intelligence service. Please use the Shopiva dashboard for live information."


def _twilio_client():
    try:
        from twilio.rest import Client
    except ImportError as exc:
        raise RuntimeError("Twilio SDK is not installed.") from exc

    account_sid = _env("TWILIO_ACCOUNT_SID")
    api_key = _env("TWILIO_API_KEY")
    api_secret = _env("TWILIO_API_SECRET")
    auth_token = _env("TWILIO_AUTH_TOKEN")

    if not account_sid:
        raise RuntimeError("TWILIO_ACCOUNT_SID is not configured.")
    if api_key and api_secret:
        return Client(api_key, api_secret, account_sid=account_sid)
    if auth_token:
        return Client(account_sid, auth_token)
    raise RuntimeError("Twilio authentication is not configured.")


def _twilio_ready():
    return _env("NIA_PHONE_CALLS_ENABLED", "false").lower() == "true" and bool(
        _env("TWILIO_ACCOUNT_SID") and _env("TWILIO_FROM_NUMBER")
        and (_env("TWILIO_AUTH_TOKEN") or (_env("TWILIO_API_KEY") and _env("TWILIO_API_SECRET")))
    )


def _twiml_gather(request, session_id, say_text):
    from twilio.twiml.voice_response import Gather, VoiceResponse

    base = _public_site_url(request)
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action=f"{base}/ai/phone/respond/{session_id}/",
        method="POST",
        language="en-KE",
        speech_timeout="auto",
        timeout=6,
    )
    gather.say(say_text)
    response.append(gather)
    response.say("I didn't hear anything. Goodbye.")
    response.hangup()
    return HttpResponse(str(response), content_type="application/xml")


@require_POST
def start_nia_call(request):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "Please sign in before asking Nia to call you."}, status=401)
    if not _twilio_ready():
        return JsonResponse({
            "ok": False,
            "error": "Nia phone calls are not configured yet. The dashboard voice assistant is available now.",
        }, status=503)

    phone = _caller_phone(request)
    if not KENYA_PHONE_RE.fullmatch(phone):
        return JsonResponse({
            "ok": False,
            "error": "Add a valid Kenyan mobile number to your Shopiva profile or default delivery address before asking Nia to call you.",
        }, status=400)

    lock_key = f"nia-call-lock:{request.user.pk}"
    if not cache.add(lock_key, "1", timeout=60):
        return JsonResponse({"ok": False, "error": "Nia is already placing a call for you. Please wait a moment."}, status=429)

    role = _role_for(request)
    session = NiaCallSession.objects.create(
        user=request.user,
        role=role,
        phone_e164=phone,
        conversation=[],
    )
    base = _public_site_url(request)

    try:
        client = _twilio_client()
        call = client.calls.create(
            to="+" + phone,
            from_=_env("TWILIO_FROM_NUMBER"),
            url=f"{base}/ai/phone/answer/{session.id}/",
            method="POST",
            status_callback=f"{base}/ai/phone/status/{session.id}/",
            status_callback_method="POST",
            status_callback_event=["initiated", "ringing", "answered", "completed"],
        )
        session.provider_sid = call.sid
        session.status = NiaCallSession.STATUS_QUEUED
        session.save(update_fields=["provider_sid", "status", "updated_at"])
    except Exception as exc:
        session.status = NiaCallSession.STATUS_FAILED
        session.last_ai_text = str(exc)[:500]
        session.save(update_fields=["status", "last_ai_text", "updated_at"])
        return JsonResponse({"ok": False, "error": "Nia could not place the phone call right now."}, status=502)
    finally:
        cache.delete(lock_key)

    return JsonResponse({"ok": True, "session_id": str(session.id), "status": session.status})


@csrf_exempt
def nia_phone_answer(request, session_id):
    session = get_object_or_404(NiaCallSession, id=session_id)
    if request.method not in {"GET", "POST"}:
        return HttpResponse(status=405)
    context = _role_context(type("Request", (), {"user": session.user})(), session.role)
    text = _opening_text(context)
    session.conversation.append({"role": "assistant", "text": text, "at": timezone.now().isoformat()})
    session.last_ai_text = text
    session.status = NiaCallSession.STATUS_IN_PROGRESS
    session.save(update_fields=["conversation", "last_ai_text", "status", "updated_at"])
    return _twiml_gather(request, session.id, text)


@csrf_exempt
def nia_phone_respond(request, session_id):
    session = get_object_or_404(NiaCallSession, id=session_id)
    if request.method != "POST":
        return HttpResponse(status=405)
    user_text = str(request.POST.get("SpeechResult", "")).strip()
    if not user_text:
        return _twiml_gather(request, session.id, "I didn't catch that. Please tell me what you need.")
    reply = _ai_reply(session, user_text)
    session.last_user_text = user_text
    session.last_ai_text = reply
    session.conversation.extend([
        {"role": "user", "text": user_text, "at": timezone.now().isoformat()},
        {"role": "assistant", "text": reply, "at": timezone.now().isoformat()},
    ])
    session.save(update_fields=["last_user_text", "last_ai_text", "conversation", "updated_at"])
    return _twiml_gather(request, session.id, reply)


@csrf_exempt
def nia_phone_status(request, session_id):
    session = get_object_or_404(NiaCallSession, id=session_id)
    status = request.POST.get("CallStatus", "").strip().lower()
    mapping = {
        "queued": NiaCallSession.STATUS_QUEUED,
        "initiated": NiaCallSession.STATUS_QUEUED,
        "ringing": NiaCallSession.STATUS_RINGING,
        "in-progress": NiaCallSession.STATUS_IN_PROGRESS,
        "completed": NiaCallSession.STATUS_COMPLETED,
        "failed": NiaCallSession.STATUS_FAILED,
        "busy": NiaCallSession.STATUS_FAILED,
        "no-answer": NiaCallSession.STATUS_NO_ANSWER,
        "canceled": NiaCallSession.STATUS_CANCELED,
    }
    new_status = mapping.get(status)
    if new_status:
        session.status = new_status
        session.save(update_fields=["status", "updated_at"])
    return HttpResponse("OK")
