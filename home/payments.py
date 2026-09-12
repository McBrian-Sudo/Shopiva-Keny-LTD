import base64
import json
import os
import urllib.error
import urllib.request
import hmac
import hashlib
import time
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .commission import get_platform_commission_percent
from .models import Order, OrderEvent, OrderItem, PaymentTransaction, Product, SellerSettlement, SellerWallet
from .notifications import notify_user


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
    request = urllib.request.Request(
        url,
        data=body,
        headers=headers or {},
        method=method or ("POST" if body else "GET"),
    )
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



def _pesapal_base_url():
    return "https://cybqa.pesapal.com/pesapalv3" if _env("PESAPAL_ENV", "sandbox").lower() == "sandbox" else "https://pay.pesapal.com/v3"


def pesapal_access_token():
    consumer_key = _env("PESAPAL_CONSUMER_KEY")
    consumer_secret = _env("PESAPAL_CONSUMER_SECRET")
    if not consumer_key or not consumer_secret:
        raise RuntimeError("Pesapal credentials are not configured.")
    status, payload = _request_json(
        f"{_pesapal_base_url()}/api/Auth/RequestToken",
        data={"consumer_key": consumer_key, "consumer_secret": consumer_secret, "grant_type": "client_credentials"},
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    )
    token = payload.get("token")
    if status != 200 or not token:
        raise RuntimeError("Pesapal authentication failed.")
    return token


def create_pesapal_checkout(order, payment):
    token = pesapal_access_token()
    ipn_id = _env("PESAPAL_IPN_ID")
    if not ipn_id:
        raise RuntimeError("PESAPAL_IPN_ID is not configured. Register Shopiva's IPN URL in Pesapal first.")
    base = _public_site_url()
    callback = f"{base}/payments/pesapal/callback/"
    cancel = f"{base}/payments/pesapal/cancel/"
    reference = f"SHOPIVA-{order.id}-{payment.id}"
    data = {
        "id": reference,
        "currency": "KES",
        "amount": float(Decimal(payment.amount)),
        "description": f"Shopiva order {order.tracking_code}",
        "callback_url": callback,
        "cancellation_url": cancel,
        "redirect_mode": "TOP_WINDOW",
        "notification_id": ipn_id,
        "billing_address": {
            "email_address": order.email,
            "phone_number": normalize_phone(order.phone),
            "country_code": "KE",
            "first_name": (order.customer_name.split() or ["Customer"])[0],
            "middle_name": "",
            "last_name": " ".join(order.customer_name.split()[1:]) or "",
            "line_1": order.address[:255],
            "line_2": "",
            "city": "",
            "state": "",
            "postal_code": "",
            "zip_code": "",
        },
    }
    status, payload = _request_json(
        f"{_pesapal_base_url()}/api/Transactions/SubmitOrderRequest",
        data=data,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json", "Content-Type": "application/json"},
    )
    redirect_url = payload.get("redirect_url")
    tracking_id = payload.get("order_tracking_id")
    if status != 200 or not redirect_url or not tracking_id:
        raise RuntimeError(payload.get("message") or "Pesapal could not create the payment session.")
    payment.provider = "pesapal"
    payment.provider_reference = str(tracking_id)
    payment.raw_response = {"order_tracking_id": tracking_id, "merchant_reference": reference}
    payment.status = "pending"
    payment.save(update_fields=["provider", "provider_reference", "raw_response", "status", "updated_at"])
    return redirect_url


def query_pesapal_payment(tracking_id):
    token = pesapal_access_token()
    status, payload = _request_json(
        f"{_pesapal_base_url()}/api/Transactions/GetTransactionStatus?orderTrackingId={tracking_id}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json", "Content-Type": "application/json"},
        method="GET",
    )
    if status != 200:
        raise RuntimeError("Unable to verify the Pesapal transaction.")
    return payload


def _finalize_pesapal_payment(payment, payload):
    with transaction.atomic():
        payment = PaymentTransaction.objects.select_for_update().get(pk=payment.pk)
        order = Order.objects.select_for_update().get(pk=payment.order_id)
        if payment.provider != "pesapal" or payment.status == "paid":
            return payment.status
        merchant_reference = str(payload.get("merchant_reference") or "")
        expected_reference = str(payment.raw_response.get("merchant_reference") or "")
        currency = str(payload.get("currency") or "").upper()
        try:
            paid_amount = Decimal(str(payload.get("amount")))
        except (InvalidOperation, TypeError, ValueError):
            paid_amount = Decimal("-1")
        if merchant_reference != expected_reference or currency != "KES" or paid_amount != Decimal(payment.amount):
            payment.status = "failed"
            payment.raw_response = {"verification_error": "Pesapal verification mismatch", "provider_response": payload}
            payment.save(update_fields=["status", "raw_response", "updated_at"])
            order.payment_status = "failed"
            order.save(update_fields=["payment_status"])
            return payment.status

        code = int(payload.get("status_code") or -1)
        if code == 1 and str(payload.get("payment_status_description", "")).upper() == "COMPLETED":
            payment.status = "paid"
            payment.provider_reference = str(payment.provider_reference)
            payment.paid_at = timezone.now()
            payment.raw_response = payload
            payment.save(update_fields=["status", "paid_at", "raw_response", "updated_at"])
            order.payment_status = "paid"
            order.status = "paid"
            order.payment_reference = str(payload.get("confirmation_code") or payment.provider_reference)
            order.paid_at = timezone.now()
            order.save(update_fields=["payment_status", "status", "payment_reference", "paid_at"])
            OrderEvent.objects.create(order=order, event_type="paid", note=f"Pesapal payment confirmed via {payload.get('payment_method') or 'online payment'}.")
            _create_seller_settlements(order)
        elif code in (2, 3):
            payment.status = "failed" if code == 2 else "cancelled"
            payment.raw_response = payload
            if not payment.inventory_released:
                _release_reserved_inventory(order)
                payment.inventory_released = True
            payment.save(update_fields=["status", "raw_response", "inventory_released", "updated_at"])
            order.payment_status = "failed"
            order.save(update_fields=["payment_status"])
        else:
            payment.status = "pending"
            payment.raw_response = payload
            payment.save(update_fields=["status", "raw_response", "updated_at"])
        return payment.status


def pesapal_callback(request):
    tracking_id = request.GET.get("OrderTrackingId", "").strip()
    merchant_reference = request.GET.get("OrderMerchantReference", "").strip()
    payment = PaymentTransaction.objects.filter(provider="pesapal", provider_reference=tracking_id).select_related("order").first()
    if not payment or not tracking_id:
        return render(request, "card_payment_result.html", {"success": False, "order": None, "error": "Payment reference could not be verified."})
    expected = str(payment.raw_response.get("merchant_reference") or "")
    if merchant_reference and merchant_reference != expected:
        return render(request, "card_payment_result.html", {"success": False, "order": payment.order, "error": "Payment reference mismatch."})
    try:
        payload = query_pesapal_payment(tracking_id)
        status = _finalize_pesapal_payment(payment, payload)
    except Exception as exc:
        status = payment.status
        payment.raw_response = {"verification_error": str(exc)}
        payment.save(update_fields=["raw_response", "updated_at"])
    if status == "paid":
        return redirect("order_success", order_id=payment.order_id)
    return render(request, "card_payment_result.html", {"success": False, "order": payment.order, "error": "Payment is not confirmed yet. Shopiva will update the order when Pesapal confirms it."})


@csrf_exempt
def pesapal_ipn(request):
    tracking_id = request.GET.get("OrderTrackingId") or request.POST.get("OrderTrackingId")
    merchant_reference = request.GET.get("OrderMerchantReference") or request.POST.get("OrderMerchantReference")
    if not tracking_id:
        return JsonResponse({"orderNotificationType": "IPNCHANGE", "status": 500})
    payment = PaymentTransaction.objects.filter(provider="pesapal", provider_reference=str(tracking_id)).first()
    if not payment:
        return JsonResponse({"orderNotificationType": "IPNCHANGE", "status": 200})
    expected = str(payment.raw_response.get("merchant_reference") or "")
    if merchant_reference and merchant_reference != expected:
        return JsonResponse({"orderNotificationType": "IPNCHANGE", "status": 500})
    try:
        payload = query_pesapal_payment(str(tracking_id))
        _finalize_pesapal_payment(payment, payload)
        return JsonResponse({"orderNotificationType": "IPNCHANGE", "orderTrackingId": tracking_id, "orderMerchantReference": merchant_reference or expected, "status": 200})
    except Exception:
        return JsonResponse({"orderNotificationType": "IPNCHANGE", "orderTrackingId": tracking_id, "orderMerchantReference": merchant_reference or expected, "status": 500})


def pesapal_cancel(request):
    tracking_id = request.GET.get("OrderTrackingId", "").strip()
    payment = PaymentTransaction.objects.filter(provider="pesapal", provider_reference=tracking_id).first()
    if payment and payment.status != "paid":
        with transaction.atomic():
            payment = PaymentTransaction.objects.select_for_update().get(pk=payment.pk)
            order = Order.objects.select_for_update().get(pk=payment.order_id)
            payment.status = "cancelled"
            if not payment.inventory_released:
                _release_reserved_inventory(order)
                payment.inventory_released = True
            payment.save(update_fields=["status", "inventory_released", "updated_at"])
            order.payment_status = "failed"
            order.save(update_fields=["payment_status"])
    return redirect("order_success", order_id=payment.order_id) if payment else redirect("checkout")


def _stripe_secret_key():
    return _env("STRIPE_SECRET_KEY")


def _stripe_webhook_secret():
    return _env("STRIPE_WEBHOOK_SECRET")


def _public_site_url():
    return _env("PUBLIC_SITE_URL", "https://shopiva-keny-ltd.onrender.com").rstrip("/")


def create_stripe_checkout_session(order, payment):
    secret = _stripe_secret_key()
    if not secret:
        raise RuntimeError("Card payments are not activated yet. Add STRIPE_SECRET_KEY in Render.")
    import requests
    success_url = f"{_public_site_url()}/payments/card/success/{order.id}/?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{_public_site_url()}/payments/card/cancel/{order.id}/"
    data = {
        "mode": "payment",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "customer_email": order.email,
        "client_reference_id": str(order.id),
        "metadata[order_id]": str(order.id),
        "metadata[payment_id]": str(payment.id),
        "line_items[0][price_data][currency]": "kes",
        "line_items[0][price_data][product_data][name]": f"Shopiva Order {order.tracking_code}",
        "line_items[0][price_data][product_data][description]": "Shopiva Kenya marketplace order",
        "line_items[0][price_data][unit_amount]": str(int(Decimal(order.total_amount) * 100)),
        "line_items[0][quantity]": "1",
    }
    response = requests.post(
        "https://api.stripe.com/v1/checkout/sessions",
        data=data,
        auth=(secret, ""),
        timeout=30,
    )
    payload = response.json()
    if response.status_code >= 400 or not payload.get("url"):
        raise RuntimeError(payload.get("error", {}).get("message") or "Stripe could not create the card checkout session.")
    payment.provider_reference = payload["id"]
    payment.raw_response = {"id": payload.get("id"), "url": payload.get("url"), "status": payload.get("status")}
    payment.status = "pending"
    payment.save(update_fields=["provider_reference", "raw_response", "status", "updated_at"])
    return payload["url"]


def _verify_stripe_signature(payload, signature_header, secret):
    if not signature_header or not secret:
        return False
    parts = {}
    for item in signature_header.split(","):
        if "=" in item:
            key, value = item.split("=", 1)
            parts.setdefault(key, []).append(value)
    try:
        timestamp = int(parts["t"][0])
        signatures = parts.get("v1", [])
    except (KeyError, ValueError):
        return False
    if abs(int(time.time()) - timestamp) > 300:
        return False
    signed = f"{timestamp}.{payload.decode('utf-8')}".encode("utf-8")
    expected = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(expected, value) for value in signatures)


def _mark_card_paid(payment_id, session_payload):
    with transaction.atomic():
        payment = PaymentTransaction.objects.select_for_update().get(pk=payment_id)
        order = Order.objects.select_for_update().get(pk=payment.order_id)
        if payment.status == "paid":
            return
        amount_total = session_payload.get("amount_total")
        currency = str(session_payload.get("currency") or "").lower()
        if amount_total != int(Decimal(payment.amount) * 100) or currency != "kes":
            payment.status = "failed"
            payment.raw_response = {"error": "Stripe amount/currency validation failed", "session": session_payload}
            payment.save(update_fields=["status", "raw_response", "updated_at"])
            order.payment_status = "failed"
            order.save(update_fields=["payment_status"])
            return
        payment.status = "paid"
        payment.provider_reference = str(session_payload.get("payment_intent") or payment.provider_reference)
        payment.paid_at = timezone.now()
        payment.raw_response = session_payload
        payment.save(update_fields=["status", "provider_reference", "paid_at", "raw_response", "updated_at"])
        order.payment_status = "paid"
        order.status = "paid"
        order.payment_reference = payment.provider_reference
        order.paid_at = timezone.now()
        order.save(update_fields=["payment_status", "status", "payment_reference", "paid_at"])
        OrderEvent.objects.create(order=order, event_type="paid", note="Card payment confirmed by Stripe.")
        _create_seller_settlements(order)


def _cancel_card_order(order):
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        payment = order.payments.filter(method="card").order_by("-created_at").first()
        if not payment or payment.status == "paid":
            return
        payment.status = "cancelled"
        if not payment.inventory_released:
            _release_reserved_inventory(order)
            payment.inventory_released = True
        payment.save(update_fields=["status", "inventory_released", "updated_at"])
        order.payment_status = "failed"
        order.save(update_fields=["payment_status"])
        OrderEvent.objects.create(order=order, event_type="cancelled", note="Card payment was cancelled.")


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
    if payment_method not in {"mpesa", "pesapal", "card", "cod"}:
        return render(request, "checkout.html", {"items": items, "total": total, "error": "Please select a valid payment method."})

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
        if request.user.is_authenticated and not request.user.is_staff:
            transaction.on_commit(
                lambda user_id=request.user.id, order_id=order.id, tracking=order.tracking_code: notify_user(
                    __import__("django.contrib.auth", fromlist=["get_user_model"]).get_user_model().objects.get(id=user_id),
                    "Order placed",
                    f"Your Shopiva order {tracking} has been placed and is awaiting payment confirmation.",
                    "order",
                    f"/account/orders/{order_id}/",
                )
            )
        for product, quantity, unit_price in locked_items:
            seller = product.seller if product.seller_id and product.seller and product.seller.is_active else None
            gross = unit_price * quantity
            commission_percent = get_platform_commission_percent(unit_price)
            commission = (gross * commission_percent / Decimal("100")).quantize(Decimal("0.01")) if seller else Decimal("0.00")
            seller_net = gross - commission
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=unit_price, seller=seller, seller_gross=gross, platform_commission=commission, seller_net=seller_net)
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

        if payment_method in {"pesapal", "card"}:
            payment = PaymentTransaction.objects.create(order=order, method="card", status="initiated", provider="pesapal", amount=final_total, phone=phone, idempotency_key=f"PESAPAL-{order.id}")
            order.payment_status = "pending"
            order.save(update_fields=["payment_status"])
            OrderEvent.objects.create(order=order, event_type="payment_pending", note="Waiting for secure Pesapal payment selection.")
        else:
            payment = PaymentTransaction.objects.create(order=order, method="mpesa", status="initiated", provider="daraja", amount=final_total, phone=normalize_phone(phone), idempotency_key=f"MPESA-{order.id}")
        order.payment_status = "pending"
        order.save(update_fields=["payment_status"])
        OrderEvent.objects.create(order=order, event_type="payment_pending", note="Waiting for M-PESA STK payment.")

    if payment_method in {"pesapal", "card"}:
        try:
            checkout_url = create_pesapal_checkout(order, payment)
        except Exception as exc:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(pk=order.pk)
                payment = PaymentTransaction.objects.select_for_update().get(pk=payment.pk)
                payment.status = "failed"
                payment.raw_response = {"error": str(exc)}
                if not payment.inventory_released:
                    _release_reserved_inventory(order)
                    payment.inventory_released = True
                payment.save(update_fields=["status", "raw_response", "inventory_released", "updated_at"])
                order.payment_status = "failed"
                order.save(update_fields=["payment_status"])
            return render(request, "checkout.html", {"items": items, "total": total, "error": str(exc)})
        request.session["cart"] = {}
        request.session["payment_order_id"] = order.id
        request.session.modified = True
        return redirect(checkout_url)

    try:
        initiate_mpesa_stk(order, payment, payment.phone)
    except Exception as exc:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order.pk)
            payment = PaymentTransaction.objects.select_for_update().get(pk=payment.pk)
            payment.status = "failed"
            payment.raw_response = {"error": str(exc)}
            if not payment.inventory_released:
                _release_reserved_inventory(order)
                payment.inventory_released = True
            payment.save(update_fields=["status", "raw_response", "inventory_released", "updated_at"])
            order.payment_status = "failed"
            order.save(update_fields=["payment_status"])
        return render(request, "checkout.html", {"items": items, "total": total, "error": f"M-PESA could not be started: {exc}"})

    request.session["cart"] = {}
    request.session["payment_order_id"] = order.id
    request.session.modified = True
    return redirect("mpesa_waiting", order_id=order.id)


@csrf_exempt
def mpesa_callback(request):
    if request.method != "POST":
        return JsonResponse({"ResultCode": 1, "ResultDesc": "POST required."}, status=405)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid JSON."}, status=400)

    callback = payload.get("Body", {}).get("stkCallback", {})
    checkout_request_id = str(callback.get("CheckoutRequestID", ""))
    result_code = callback.get("ResultCode")
    result_desc = callback.get("ResultDesc", "")
    payment = PaymentTransaction.objects.filter(checkout_request_id=checkout_request_id, method="mpesa").first()
    if not payment:
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

    with transaction.atomic():
        payment = PaymentTransaction.objects.select_for_update().get(pk=payment.pk)
        order = Order.objects.select_for_update().get(pk=payment.order_id)
        payment.raw_response = payload

        if str(result_code) == "0":
            if payment.status == "paid":
                return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

            metadata = {
                item.get("Name"): item.get("Value")
                for item in callback.get("CallbackMetadata", {}).get("Item", [])
                if isinstance(item, dict) and item.get("Name")
            }
            receipt = str(metadata.get("MpesaReceiptNumber") or "").strip()
            callback_amount = metadata.get("Amount")
            callback_phone = normalize_phone(metadata.get("PhoneNumber") or "")
            expected_phone = normalize_phone(payment.phone)
            try:
                amount_matches = Decimal(str(callback_amount)).quantize(Decimal("0.01")) == Decimal(payment.amount).quantize(Decimal("0.01"))
            except Exception:
                amount_matches = False

            # A positive-looking callback is not enough. A payment becomes paid
            # only when the provider supplies the receipt and matches the amount
            # and phone recorded for this transaction.
            if not receipt or not amount_matches or callback_phone != expected_phone:
                payment.status = "pending"
                payment.provider_reference = receipt
                payment.paid_at = None
                payment.raw_response = {
                    **payload,
                    "shopiva_validation": {
                        "receipt_present": bool(receipt),
                        "amount_matches": amount_matches,
                        "phone_matches": callback_phone == expected_phone,
                    },
                }
                payment.save(update_fields=["status", "provider_reference", "paid_at", "raw_response", "updated_at"])
                return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

            payment.status = "paid"
            payment.provider_reference = receipt
            payment.paid_at = timezone.now()
            order.payment_status = "paid"
            order.status = "paid"
            order.payment_reference = receipt
            order.paid_at = timezone.now()
            order.save(update_fields=["payment_status", "status", "payment_reference", "paid_at"])
            OrderEvent.objects.create(order=order, event_type="paid", note=f"M-PESA payment confirmed: {receipt}")
            _create_seller_settlements(order)

            customer_id = None
            seller_ids = []
            if order.email:
                from django.contrib.auth.models import User
                customer = User.objects.filter(email__iexact=order.email, is_active=True).first()
                customer_id = customer.id if customer else None
            seller_ids = [item.seller.user_id for item in order.items.select_related("seller", "seller__user") if item.seller_id and item.seller]
            tracking = order.tracking_code
            order_id = order.id
            seller_ids = list(dict.fromkeys(seller_ids))
            transaction.on_commit(
                lambda customer_id=customer_id, seller_ids=seller_ids, tracking=tracking, order_id=order_id, receipt=receipt: _send_payment_notifications(
                    customer_id, seller_ids, tracking, order_id, receipt
                )
            )
        else:
            payment.status = "failed"
            if not payment.inventory_released:
                _release_reserved_inventory(order)
                payment.inventory_released = True
            order.payment_status = "failed"
            order.save(update_fields=["payment_status"])
            OrderEvent.objects.create(order=order, event_type="cancelled", note=f"M-PESA payment failed: {result_desc}")

        payment.save(update_fields=["status", "provider_reference", "paid_at", "raw_response", "inventory_released", "updated_at"])

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


def _send_payment_notifications(customer_id, seller_ids, tracking, order_id, receipt):
    from django.contrib.auth.models import User
    if customer_id:
        customer = User.objects.filter(id=customer_id).first()
        if customer:
            notify_user(
                customer,
                "M-PESA payment confirmed",
                f"Your Shopiva order {tracking} is confirmed. M-PESA receipt: {receipt}",
                "payment",
                f"/account/orders/{order_id}/",
            )
    for seller_id in seller_ids:
        seller_user = User.objects.filter(id=seller_id, is_active=True).first()
        if seller_user:
            notify_user(
                seller_user,
                "Order payment confirmed",
                f"Payment for order {tracking} is confirmed. Your seller earnings are now pending delivery.",
                "payment",
                "/seller/",
            )


def _release_reserved_inventory(order):
    for item in order.items.select_related("product").select_for_update():
        product = item.product
        product.stock_quantity += item.quantity
        product.save(update_fields=["stock_quantity"])


def _create_seller_settlements(order):
    seller_totals = {}
    for item in order.items.select_related("seller"):
        if not item.seller_id or not item.seller or not item.seller.is_active:
            continue
        data = seller_totals.setdefault(
            item.seller_id,
            {"seller": item.seller, "gross": Decimal("0.00"), "commission": Decimal("0.00"), "net": Decimal("0.00")},
        )
        data["gross"] += item.seller_gross
        data["commission"] += item.platform_commission
        data["net"] += item.seller_net

    for data in seller_totals.values():
        settlement, created = SellerSettlement.objects.get_or_create(
            order=order,
            seller=data["seller"],
            defaults={
                "gross_amount": data["gross"],
                "platform_commission": data["commission"],
                "seller_amount": data["net"],
                "status": "pending",
            },
        )
        if created:
            wallet, _ = SellerWallet.objects.get_or_create(seller=data["seller"])
            wallet.pending_balance += data["net"]
            wallet.total_sales += data["gross"]
            wallet.total_commission += data["commission"]
            wallet.save(update_fields=["pending_balance", "total_sales", "total_commission", "updated_at"])



def card_payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    allowed = request.session.get("payment_order_id") == order.id or (request.user.is_authenticated and (request.user.is_staff or order.email.lower() == request.user.email.lower()))
    if not allowed:
        return JsonResponse({"ok": False, "error": "You are not authorized to view this payment."}, status=403)
    request.session["payment_order_id"] = order.id
    request.session.modified = True
    return render(request, "card_payment_result.html", {"order": order, "success": order.payment_status == "paid"})


def card_payment_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    allowed = request.session.get("payment_order_id") == order.id or (request.user.is_authenticated and (request.user.is_staff or order.email.lower() == request.user.email.lower()))
    if not allowed:
        return JsonResponse({"ok": False, "error": "You are not authorized to cancel this payment."}, status=403)
    _cancel_card_order(order)
    return redirect("order_success", order_id=order.id)

@csrf_exempt
def stripe_webhook(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)
    secret = _stripe_webhook_secret()
    if not secret or not _verify_stripe_signature(request.body, request.headers.get("Stripe-Signature", ""), secret):
        return JsonResponse({"ok": False, "error": "Invalid webhook signature."}, status=400)
    try:
        event = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid JSON."}, status=400)
    if event.get("type") == "checkout.session.completed":
        session = event.get("data", {}).get("object", {})
        metadata = session.get("metadata", {})
        payment_id = metadata.get("payment_id")
        if payment_id:
            try:
                _mark_card_paid(int(payment_id), session)
            except (PaymentTransaction.DoesNotExist, Order.DoesNotExist, ValueError):
                return JsonResponse({"ok": False, "error": "Payment transaction not found."}, status=404)
    return JsonResponse({"received": True})


def mpesa_payment_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    allowed = bool(
        request.session.get("payment_order_id") == order.id
        or (request.user.is_authenticated and (request.user.is_staff or order.email.lower() == request.user.email.lower()))
    )
    if not allowed:
        return JsonResponse({"ok": False, "error": "You are not authorized to view this payment."}, status=403)
    payment = order.payments.filter(method="mpesa").order_by("-created_at").first()
    return JsonResponse({"ok": True, "order_id": order.id, "payment_status": order.payment_status, "order_status": order.status, "reference": order.payment_reference, "transaction_status": payment.status if payment else None})


def mpesa_waiting(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    allowed = bool(
        request.session.get("payment_order_id") == order.id
        or (request.user.is_authenticated and (request.user.is_staff or order.email.lower() == request.user.email.lower()))
    )
    if not allowed:
        return JsonResponse({"ok": False, "error": "You are not authorized to view this payment."}, status=403)
    request.session["payment_order_id"] = order.id
    request.session.modified = True
    return render(request, "mpesa_waiting.html", {"order": order})
