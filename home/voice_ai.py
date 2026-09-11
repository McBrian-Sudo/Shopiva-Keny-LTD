import json
import os
import tempfile
import urllib.request
import uuid

from django.contrib.auth.decorators import login_required
from django.http import FileResponse, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .ai import _catalog
from .models import Order, Product, PaymentTransaction


def _openai_multipart_sdp(sdp, session):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    boundary = "----ShopivaRealtime" + uuid.uuid4().hex
    parts = []
    parts.append(
        f"--{boundary}\r\n"
        "Content-Disposition: form-data; name=\"sdp\"; filename=\"offer.sdp\"\r\n"
        "Content-Type: application/sdp\r\n\r\n"
    )
    parts.append(sdp)
    parts.append("\r\n")
    parts.append(
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="session"\r\n'
        "Content-Type: application/json\r\n\r\n"
    )
    parts.append(json.dumps(session))
    parts.append(f"\r\n--{boundary}--\r\n")
    body = "".join(parts).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/realtime/calls",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")


def _catalog_context():
    return [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "description": p.description[:350],
            "price": str(p.discounted_price),
            "original_price": str(p.price),
            "discount_percent": p.discount_percent,
            "stock": p.stock_quantity,
        }
        for p in _catalog(30)
    ]


def _product_payload(product):
    return {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "description": product.description[:350],
        "price": str(product.discounted_price),
        "original_price": str(product.price),
        "discount_percent": product.discount_percent,
        "stock": product.stock_quantity,
    }


def _search_products(query="", category="", max_price=None):
    products = _catalog(120)
    words = {w.lower() for w in query.split() if len(w) > 2}
    ranked = []
    for product in products:
        haystack = f"{product.name} {product.category} {product.description} {product.promo_text}".lower()
        score = sum(2 if w in product.name.lower() else 1 for w in words if w in haystack)
        if category and category.lower() not in product.category.lower():
            continue
        if max_price is not None and product.discounted_price > max_price:
            continue
        if score or not words:
            ranked.append((score, product))
    ranked.sort(key=lambda item: (-item[0], -item[1].discount_percent, item[1].discounted_price))
    return [_product_payload(p) for _, p in ranked[:8]]


def _customer_instructions(request):
    catalog = _catalog_context()
    customer = "Guest customer. You may help them browse and add available products to their session cart."
    if request.user.is_authenticated and not request.user.is_staff:
        orders = list(
            Order.objects.filter(email__iexact=request.user.email)
            .order_by("-created_at")
            .values("id", "tracking_code", "status", "payment_status", "total_amount")[:8]
        )
        customer = f"Authenticated customer. Their recent orders are: {json.dumps(orders, default=str)}."
    return f"""
You are Shopiva Voice, the natural voice shopping assistant for Shopiva Kenya.
Speak naturally and briefly. Use KSh for prices.
The customer may interrupt you. Listen carefully and continue the conversation.
You can help discover products, compare options, explain discounts, add products to the cart, and check the customer's own order status.
Never invent products, prices, stock, discounts, order status, or payment results.
Only recommend products from the catalogue below.
If the customer says "the second one", "that one", or similar, use the products you just discussed.
Never claim an M-PESA payment is successful unless the recorded payment status is exactly paid.
{customer}
CATALOG:
{json.dumps(catalog, ensure_ascii=False)}
"""


def _admin_instructions():
    catalog = _catalog_context()
    payments = list(
        PaymentTransaction.objects.filter(method="mpesa")
        .order_by("-created_at")
        .values("id", "order_id", "status", "amount", "provider_reference", "created_at")[:20]
    )
    orders = list(
        Order.objects.order_by("-created_at")
        .values("id", "tracking_code", "status", "payment_status", "total_amount", "email")[:20]
    )
    return f"""
You are Shopiva Admin Voice, the voice operations assistant for Shopiva Kenya.
Speak clearly, concisely and professionally.
Answer using only the supplied Shopiva data.
You can explain products, stock, orders, delivery and M-PESA operations.
Never invent data.
For M-PESA, a payment is successful ONLY when status is exactly paid. Pending is not successful.
M-PESA snapshot:
{json.dumps(payments, default=str)}
Recent orders:
{json.dumps(orders, default=str)}
Product catalogue:
{json.dumps(catalog, ensure_ascii=False)}
"""


@csrf_exempt
def realtime_call(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    if not os.getenv("OPENAI_API_KEY", "").strip():
        return JsonResponse({"ok": False, "error": "Voice AI is not configured yet."}, status=503)

    if request.user.is_authenticated and request.user.is_staff:
        instructions = _admin_instructions()
        tools = [
            {
                "type": "function",
                "name": "get_mpesa_attention",
                "description": "Return the latest M-PESA transactions that are pending or failed. Never treat pending as paid.",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
            },
            {
                "type": "function",
                "name": "get_low_stock",
                "description": "Return active products with low stock so the admin can act before they sell out.",
                "parameters": {
                    "type": "object",
                    "properties": {"threshold": {"type": "integer", "minimum": 0, "maximum": 100}},
                    "additionalProperties": False
                }
            },
            {
                "type": "function",
                "name": "get_order_attention",
                "description": "Return recent orders that need operational attention, including unpaid, pending-payment, failed-payment, or cancelled orders.",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False}
            }
        ]
    else:
        instructions = _customer_instructions(request)
        tools = [
            {
                "type": "function",
                "name": "search_products",
                "description": "Search the live Shopiva product catalogue using a natural-language request.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "category": {"type": "string"},
                        "max_price": {"type": "number"}
                    },
                    "additionalProperties": False
                }
            },
            {
                "type": "function",
                "name": "get_cart_summary",
                "description": "Read the current browser cart and return its real contents and total.",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False}
            },
            {
                "type": "function",
                "name": "get_product_details",
                "description": "Return current details for one real Shopiva product.",
                "parameters": {
                    "type": "object",
                    "properties": {"product_id": {"type": "integer"}},
                    "required": ["product_id"],
                    "additionalProperties": False
                }
            },
            {
                "type": "function",
                "name": "add_to_cart",
                "description": "Add a real Shopiva product to the current customer's browser cart. Use only a product id from the live catalogue.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "integer"},
                        "quantity": {"type": "integer", "minimum": 1, "maximum": 20}
                    },
                    "required": ["product_id", "quantity"],
                    "additionalProperties": False
                }
            },
            {
                "type": "function",
                "name": "get_my_order_status",
                "description": "Check the authenticated customer's own order status. Never expose another customer's order.",
                "parameters": {
                    "type": "object",
                    "properties": {"order_id": {"type": "integer"}},
                    "required": ["order_id"],
                    "additionalProperties": False
                }
            }
        ]

    session = {
        "type": "realtime",
        "model": os.getenv("OPENAI_REALTIME_MODEL", "gpt-realtime-2.1"),
        "output_modalities": ["audio"],
        "audio": {
            "input": {"turn_detection": {"type": "semantic_vad", "eagerness": "auto"}},
            "output": {"voice": os.getenv("OPENAI_REALTIME_VOICE", "marin")},
        },
        "instructions": instructions,
        "tools": tools,
        "max_output_tokens": 700,
    }

    try:
        answer_sdp = _openai_multipart_sdp(request.body.decode("utf-8"), session)
        return HttpResponse(answer_sdp, content_type="application/sdp")
    except Exception:
        return JsonResponse({"ok": False, "error": "Could not start the realtime voice session."}, status=502)


@require_POST
def realtime_action(request):
    if not request.user.is_authenticated and request.POST.get("action") == "get_my_order_status":
        return JsonResponse({"ok": False, "error": "Please sign in to check your orders."}, status=401)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        payload = request.POST

    action = payload.get("action")
    if action == "search_products":
        max_price = payload.get("max_price")
        try:
            max_price = float(max_price) if max_price not in (None, "") else None
        except (TypeError, ValueError):
            max_price = None
        return JsonResponse({"ok": True, "products": _search_products(
            str(payload.get("query", "")),
            str(payload.get("category", "")),
            max_price,
        )})

    if action == "get_product_details":
        try:
            product_id = int(payload.get("product_id"))
        except (TypeError, ValueError):
            return JsonResponse({"ok": False, "error": "Invalid product id."}, status=400)
        product = Product.objects.filter(id=product_id, is_active=True).first()
        if not product:
            return JsonResponse({"ok": False, "error": "That product is not available."}, status=404)
        return JsonResponse({"ok": True, "product": _product_payload(product)})

    if action == "get_cart_summary":
        cart = request.session.get("cart", {})
        items = []
        total = 0
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=int(product_id), is_active=True)
                qty = max(1, int(quantity))
            except (Product.DoesNotExist, TypeError, ValueError):
                continue
            line_total = product.discounted_price * qty
            total += line_total
            items.append({
                "product_id": product.id,
                "name": product.name,
                "quantity": qty,
                "unit_price": str(product.discounted_price),
                "line_total": str(line_total),
            })
        return JsonResponse({"ok": True, "items": items, "total": str(total)})

    if action == "add_to_cart":
        try:
            product_id = int(payload.get("product_id"))
            quantity = max(1, min(int(payload.get("quantity", 1)), 20))
        except (TypeError, ValueError):
            return JsonResponse({"ok": False, "error": "Invalid product or quantity."}, status=400)

        product = Product.objects.filter(id=product_id, is_active=True).first()
        if not product:
            return JsonResponse({"ok": False, "error": "That product is no longer available."}, status=404)

        cart = request.session.get("cart", {})
        current = int(cart.get(str(product.id), 0))
        new_quantity = min(current + quantity, product.stock_quantity)
        if new_quantity <= current:
            return JsonResponse({"ok": False, "error": f"{product.name} does not have enough stock."}, status=409)

        cart[str(product.id)] = new_quantity
        request.session["cart"] = cart
        request.session.modified = True
        return JsonResponse({"ok": True, "message": f"Added {quantity} {product.name} to your cart.", "product": product.name, "quantity": new_quantity})

    if action == "get_my_order_status":
        try:
            order_id = int(payload.get("order_id"))
        except (TypeError, ValueError):
            return JsonResponse({"ok": False, "error": "Invalid order id."}, status=400)

        order = Order.objects.filter(id=order_id, email__iexact=request.user.email).first()
        if not order:
            return JsonResponse({"ok": False, "error": "That order was not found in your account."}, status=404)
        return JsonResponse(
            {
                "ok": True,
                "order_id": order.id,
                "tracking_code": order.tracking_code,
                "status": order.get_status_display(),
                "payment_status": order.get_payment_status_display(),
            }
        )

    if action == "get_low_stock":
        if not request.user.is_staff:
            return JsonResponse({"ok": False, "error": "Admin access required."}, status=403)
        try:
            threshold = max(0, min(int(payload.get("threshold", 5)), 100))
        except (TypeError, ValueError):
            threshold = 5
        rows = list(
            Product.objects.filter(is_active=True, stock_quantity__lte=threshold)
            .order_by("stock_quantity", "name")
            .values("id", "name", "stock_quantity", "price", "discount_percent")[:30]
        )
        return JsonResponse({"ok": True, "products": rows})

    if action == "get_order_attention":
        if not request.user.is_staff:
            return JsonResponse({"ok": False, "error": "Admin access required."}, status=403)
        rows = list(
            Order.objects.filter(
                payment_status__in=["unpaid", "pending", "failed"]
            ).exclude(status="cancelled").order_by("-created_at")
            .values("id", "tracking_code", "status", "payment_status", "total_amount", "email", "created_at")[:30]
        )
        return JsonResponse({"ok": True, "orders": rows})

    if action == "get_mpesa_attention":
        if not request.user.is_staff:
            return JsonResponse({"ok": False, "error": "Admin access required."}, status=403)
        rows = list(
            PaymentTransaction.objects.filter(method="mpesa", status__in=["pending", "failed"])
            .order_by("-created_at")
            .values("id", "order_id", "status", "amount", "provider_reference")[:20]
        )
        return JsonResponse({"ok": True, "transactions": rows})

    return JsonResponse({"ok": False, "error": "Unknown voice action."}, status=400)


def transcribe_voice(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)
    if not os.getenv("OPENAI_API_KEY", "").strip():
        return JsonResponse({"ok": False, "error": "Voice AI is not configured yet."}, status=503)
    audio = request.FILES.get("audio")
    if not audio:
        return JsonResponse({"ok": False, "error": "No voice recording was received."}, status=400)
    if audio.size > 10 * 1024 * 1024:
        return JsonResponse({"ok": False, "error": "Voice recording is too large. Please keep it under 10 MB."}, status=400)
    suffix = ".webm"
    name = (audio.name or "").lower()
    if "." in name:
        suffix = "." + name.rsplit(".", 1)[-1][:8]
    try:
        from openai import OpenAI
        with tempfile.NamedTemporaryFile(suffix=suffix) as temp:
            for chunk in audio.chunks():
                temp.write(chunk)
            temp.flush()
            with open(temp.name, "rb") as voice_file:
                transcript = OpenAI(api_key=os.getenv("OPENAI_API_KEY")).audio.transcriptions.create(
                    model=os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe"),
                    file=voice_file,
                )
        return JsonResponse({"ok": True, "text": getattr(transcript, "text", "").strip()})
    except Exception:
        return JsonResponse({"ok": False, "error": "I could not understand that recording. Please try again."}, status=502)


def speak_text(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)
    if not os.getenv("OPENAI_API_KEY", "").strip():
        return JsonResponse({"ok": False, "error": "Voice AI is not configured yet."}, status=503)
    text = request.POST.get("text", "").strip()[:2500]
    if not text:
        return JsonResponse({"ok": False, "error": "No text was supplied."}, status=400)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp:
            output_path = temp.name
        speech = client.audio.speech.create(
            model=os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
            voice=os.getenv("OPENAI_TTS_VOICE", "alloy"),
            input=text,
            response_format="mp3",
        )
        speech.write_to_file(output_path)
        return FileResponse(open(output_path, "rb"), as_attachment=False, filename="shopiva-ai.mp3", content_type="audio/mpeg")
    except Exception:
        return JsonResponse({"ok": False, "error": "Voice feedback is temporarily unavailable."}, status=502)
