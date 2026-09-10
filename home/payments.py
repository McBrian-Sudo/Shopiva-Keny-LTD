import base64
import json
import os
import urllib.error
import urllib.request
from datetime import datetime
from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Order, OrderEvent, OrderItem, PaymentTransaction, Product


def _env(name, default=""):
    return os.environ.get(name, default).strip()


def _base_url():
    return "https://sandbox.safaricom.co.ke" if _env("MPESA_ENV", "sandbox").lower() == "sandbox" else "https://api.safaricom.co.ke"


def _shortcode():
    return _env("MPESA_SHORTCODE") or (_env("MPESA_TILL_NUMBER") if _env("MPESA_ENV", "sandbox").lower() == "production" else "174379")


def _passkey():
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
        raise RuntimeError("M-PESA shortcode/passkey is not configured. Add MPESA_PASSKEY to Render.")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()
    amount = max(1, int(Decimal(order.total_amount).quantize(Decimal("1"))))
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
    if status not in (200, 201) or str(response.get("ResponseCode", "0")) != "0":
        raise RuntimeError(response.get("errorMessage") or response.get("ResponseDescription") or str(response))
    payment.merchant_request_id = response.get("MerchantRequestID", "")
    payment.checkout_request_id = response.get("CheckoutRequestID", "")
    payment.status = "pending"
    payment.save(update_fields=["merchant_request_id", "checkout_request_id", "status", "updated_at"])
    return response


def checkout_mpesa(request):
    cart_data = request.session.get("cart", {})
    items = []
    total = Decimal("0.00")
    for product_id, raw_quantity in cart_data.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            quantity = min(max(0, int(raw_quantity)), product.stock_quantity)
        except (Product.DoesNotExist, TypeError, ValueError):
            continue
        if quantity <= 0:
            continue
        subtotal = product.discounted_price * quantity
        total += subtotal
        items.append({"product": product, "quantity": quantity, "subtotal": subtotal, "unit_price": product.discounted_price})

    if request.method != "POST":
        return render(request, "checkout.html", {"items": items, "total": total})

    customer_name = request.POST.get("customer_name", "").strip()
    email = request.POST.get("email", "").strip()
    phone = request.POST.get("phone", "").strip()
    address = request.POST.get("address", "").strip()
    payment_method = request.POST.get("payment_method", "mpesa").strip().lower()

    if not all([customer_name, email, phone, address]) or not items:
        return render(request, "checkout.html", {"items": items, "total": total, "error": "Please complete all customer details and make sure your cart is not empty."})
    if payment_method not in {"mpesa", "cod"}:
        return render(request, "checkout.html", {"items": items, "total": total, "error": "Card payments will be enabled after the M-PESA flow is verified."})

    with transaction.atomic():
        locked_items = []
        final_total = Decimal("0.00")
        for item in items:
            product = Product.objects.select_for_update().get(id=item["product"].id)
            quantity = item["quantity"]
            if not product.is_active or product.stock_quantity < quantity:
                return render(request, "checkout.html", {"items": items, "total": total, "error": f"Sorry, {product.name} no longer has enough stock."})
            unit_price = product.discounted_price
            final_total += unit_price * quantity
            locked_items.append((product, quantity, unit_price))

        order = Order.objects.create(
            customer_name=customer_name,
            email=email,
            phone=phone,
            address=address,
            total_amount=final_total,
            status="pending",
            payment_status="unpaid",
            tracking_code=f"SPV-{__import__('uuid').uuid4().hex[:10].upper()}",
        )
        OrderEvent.objects.create(order=order, event_type="placed", note="Order placed through Shopiva checkout.", actor=request.user if request.user.is_authenticated else None)
        for product, quantity, unit_price in locked_items:
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=unit_price)
            product.stock_quantity -= quantity
            product.save(update_fields=["stock_quantity"])

        if payment_method == "cod":
            PaymentTransaction.objects.create(order=order, method="cod", status="pending", provider="shopiva", amount=final_total, phone=phone, idempotency_key=f"COD-{order.id}")
            order.payment_status = "pending"
            order.status = "confirmed"
            order.save(update_fields=["payment_status", "status"])
            OrderEvent.objects.create(order=order, event_type="confirmed", note="Cash on Delivery order accepted.")
            request.session["cart"] = {}
            request.session.modified = True
            return redirect("order_success", order_id=order.id)

        payment = PaymentTransaction.objects.create(order=order, method="mpesa", status="initiated", provider="daraja", amount=final_total, phone=normalize_phone(phone), idempotency_key=f"MPESA-{order.id}")
        order.payment_status = "pending"
        order.save(update_fields=["payment_status"])
        OrderEvent.objects.create(order=order, event_type="payment_pending", note="Waiting for M-PESA STK payment.")

    try:
        initiate_mpesa_stk(order, payment, payment.phone)
    except Exception as exc:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order.pk)
            payment = PaymentTransaction.objects.select_for_update().get(pk=payment.pk)
            payment.status = "failed"
            payment.raw_response = {"error": str(exc)}
            payment.save(update_fields=["status", "raw_response", "updated_at"])
            order.payment_status = "failed"
            order.save(update_fields=["payment_status"])
        return render(request, "checkout.html", {"items": items, "total": total, "error": f"M-PESA could not be started: {exc}"})

    request.session["cart"] = {}
    request.session.modified = True
    return redirect("mpesa_waiting", order_id=order.id)


def create_mpesa_payment(request, order_id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)
    order = get_object_or_404(Order, id=order_id)
    if order.payment_status == "paid":
        return JsonResponse({"ok": True, "status": "paid"})
    phone = normalize_phone(request.POST.get("phone") or order.phone)
    if not phone.startswith("254") or len(phone) != 12:
        return JsonResponse({"ok": False, "error": "Enter a valid Kenyan phone number."}, status=400)
    payment = PaymentTransaction.objects.create(order=order, method="mpesa", status="initiated", provider="daraja", amount=order.total_amount, phone=phone, idempotency_key=f"MPESA-{order.id}-{timezone.now().strftime('%Y%m%d%H%M%S%f')}")
    order.payment_status = "pending"
    order.save(update_fields=["payment_status"])
    try:
        response = initiate_mpesa_stk(order, payment, phone)
    except Exception as exc:
        payment.status = "failed"
        payment.raw_response = {"error": str(exc)}
        payment.save(update_fields=["status", "raw_response", "updated_at"])
        order.payment_status = "failed"
        order.save(update_fields=["payment_status"])
        return JsonResponse({"ok": False, "error": str(exc)}, status=502)
    return JsonResponse({"ok": True, "status": "pending", "message": response.get("CustomerMessage", "STK prompt sent."), "checkout_request_id": payment.checkout_request_id})


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
            OrderEvent.objects.create(order=order, event_type="paid", note=f"M-PESA payment confirmed: {receipt}")
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
    return JsonResponse({"ok": True, "order_id": order.id, "payment_status": order.payment_status, "order_status": order.status, "reference": order.payment_reference, "transaction_status": payment.status if payment else None})


def mpesa_waiting(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "mpesa_waiting.html", {"order": order})
