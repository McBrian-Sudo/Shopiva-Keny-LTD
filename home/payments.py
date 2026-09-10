import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Order, OrderEvent, PaymentTransaction


SANDBOX_SHORTCODE = "174379"
SANDBOX_PASSKEY = "bfb279f9aa9bdbcf3e36f1a6e6c5b8c2f7c8e5d5c5e4c2f0"


def _env(name, default=""):
    return os.environ.get(name, default).strip()


def _base_url():
    return "https://sandbox.safaricom.co.ke" if _env("MPESA_ENV", "sandbox").lower() == "sandbox" else "https://api.safaricom.co.ke"


def _shortcode():
    if _env("MPESA_ENV", "sandbox").lower() == "sandbox":
        return _env("MPESA_SHORTCODE", SANDBOX_SHORTCODE)
    return _env("MPESA_SHORTCODE") or _env("MPESA_TILL_NUMBER")


def _passkey():
    if _env("MPESA_ENV", "sandbox").lower() == "sandbox":
        return _env("MPESA_PASSKEY", SANDBOX_PASSKEY)
    return _env("MPESA_PASSKEY")


def _callback_url():
    return _env("MPESA_CALLBACK_URL", "https://shopiva-keny-ltd.onrender.com/payments/mpesa/callback/")


def normalize_phone(phone):
    value = "".join(ch for ch in str(phone) if ch.isdigit() or ch == "+")
    if value.startswith("+254"):
        return "254" + value[4:]
    if value.startswith("254"):
        return value
    if value.startswith("0") and len(value) == 10:
        return "254" + value[1:]
    return value


def _request_json(url, data=None, headers=None, method=None):
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8") if isinstance(data, (dict, list)) else data
    request = urllib.request.Request(url, data=body, headers=headers or {}, method=method or ("POST" if body else "GET"))
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"error": raw}
        return exc.code, payload
    except Exception as exc:
        return 0, {"error": str(exc)}


def daraja_access_token():
    key = _env("MPESA_CONSUMER_KEY")
    secret = _env("MPESA_CONSUMER_SECRET")
    if not key or not secret:
        raise RuntimeError("MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET are not configured.")

    auth = base64.b64encode(f"{key}:{secret}".encode()).decode()
    status, payload = _request_json(
        f"{_base_url()}/oauth/v1/generate?grant_type=client_credentials",
        headers={"Authorization": f"Basic {auth}"},
        method="GET",
    )
    token = payload.get("access_token")
    if status != 200 or not token:
        raise RuntimeError(f"Daraja authentication failed: {payload}")
    return token


def initiate_mpesa_stk(order, payment, phone):
    token = daraja_access_token()
    shortcode = _shortcode()
    passkey = _passkey()
    if not shortcode or not passkey:
        raise RuntimeError("M-PESA shortcode/passkey is not configured.")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()
    amount = int(Decimal(order.total_amount).quantize(Decimal("1")))

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": _callback_url(),
        "AccountReference": f"SHOPIVA-{order.id}",
        "TransactionDesc": f"Shopiva order {order.id}",
    }

    status, response = _request_json(
        f"{_base_url()}/mpesa/stkpush/v1/processrequest",
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    payment.raw_response = response
    payment.updated_at = timezone.now()
    payment.save(update_fields=["raw_response", "updated_at"])

    if status not in (200, 201) or response.get("ResponseCode") not in (None, "0", 0):
        raise RuntimeError(response.get("errorMessage") or response.get("ResponseDescription") or str(response))

    payment.merchant_request_id = response.get("MerchantRequestID", "")
    payment.checkout_request_id = response.get("CheckoutRequestID", "")
    payment.status = "pending"
    payment.save(update_fields=["merchant_request_id", "checkout_request_id", "status", "updated_at"])
    return response


def create_mpesa_payment(request, order_id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    order = get_object_or_404(Order, id=order_id)
    if order.payment_status == "paid":
        return JsonResponse({"ok": True, "status": "paid", "message": "This order is already paid."})

    phone = normalize_phone(request.POST.get("phone") or order.phone)
    if not phone.startswith("254") or len(phone) != 12:
        return JsonResponse({"ok": False, "error": "Enter a valid Kenyan phone number, e.g. 0712345678."}, status=400)

    payment = PaymentTransaction.objects.create(
        order=order,
        method="mpesa",
        status="initiated",
        provider="daraja",
        amount=order.total_amount,
        phone=phone,
        idempotency_key=f"MPESA-{order.id}-{timezone.now().strftime('%Y%m%d%H%M%S%f')}",
    )

    order.payment_status = "pending"
    order.status = "pending"
    order.save(update_fields=["payment_status", "status"])
    OrderEvent.objects.create(order=order, event_type="payment_pending", note="M-PESA STK payment initiated.")

    try:
        response = initiate_mpesa_stk(order, payment, phone)
    except Exception as exc:
        payment.status = "failed"
        payment.raw_response = {"error": str(exc)}
        payment.save(update_fields=["status", "raw_response", "updated_at"])
        order.payment_status = "failed"
        order.save(update_fields=["payment_status"])
        OrderEvent.objects.create(order=order, event_type="cancelled", note="M-PESA initiation failed.")
        return JsonResponse({"ok": False, "error": str(exc)}, status=502)

    return JsonResponse({"ok": True, "status": "pending", "message": response.get("CustomerMessage", "STK prompt sent. Check your phone."), "checkout_request_id": payment.checkout_request_id})


@csrf_exempt
def mpesa_callback(request):
    if request.method != "POST":
        return JsonResponse({"ResultCode": 1, "ResultDesc": "POST required."}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid JSON."}, status=400)

    callback = payload.get("Body", {}).get("stkCallback", {})
    checkout_request_id = callback.get("CheckoutRequestID", "")
    result_code = callback.get("ResultCode")
    result_desc = callback.get("ResultDesc", "")

    payment = PaymentTransaction.objects.filter(checkout_request_id=checkout_request_id).first()
    if not payment:
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

    with transaction.atomic():
        payment = PaymentTransaction.objects.select_for_update().get(pk=payment.pk)
        order = Order.objects.select_for_update().get(pk=payment.order_id)
        payment.raw_response = payload

        if str(result_code) == "0":
            metadata = {item.get("Name"): item.get("Value") for item in callback.get("CallbackMetadata", {}).get("Item", [])}
            receipt = str(metadata.get("MpesaReceiptNumber", ""))
            payment.status = "paid"
            payment.provider_reference = receipt
            payment.paid_at = timezone.now()
            order.payment_status = "paid"
            order.status = "paid"
            order.payment_reference = receipt
            order.paid_at = timezone.now()
            order.save(update_fields=["payment_status", "status", "payment_reference", "paid_at"])
            OrderEvent.objects.create(order=order, event_type="paid", note=f"M-PESA payment confirmed{': ' + receipt if receipt else '.'}")
        else:
            payment.status = "failed"
            order.payment_status = "failed"
            order.save(update_fields=["payment_status"])
            OrderEvent.objects.create(order=order, event_type="cancelled", note=f"M-PESA payment failed: {result_desc}")

        payment.save(update_fields=["status", "provider_reference", "paid_at", "raw_response", "updated_at"])

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


def mpesa_payment_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    payment = order.payments.filter(method="mpesa").order_by("-created_at").first()
    return JsonResponse({
        "ok": True,
        "order_id": order.id,
        "payment_status": order.payment_status,
        "order_status": order.status,
        "reference": order.payment_reference,
        "transaction_status": payment.status if payment else None,
    })


def mpesa_waiting(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "mpesa_waiting.html", {"order": order})
