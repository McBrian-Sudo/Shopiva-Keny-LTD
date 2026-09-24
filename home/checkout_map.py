from decimal import Decimal, InvalidOperation
import re

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render

from .models import Order
from .payments import checkout_mpesa as original_checkout_mpesa
from .delivery_pricing import calculate_order_quote, tariff_text
from .models import DeliveryTariff


def _coord(value, low, high):
    try:
        value = Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError, AttributeError):
        return None
    return value.quantize(Decimal("0.000001")) if low <= value <= high else None



def checkout_quote(request):
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "GET required."}, status=405)
    try:
        latitude = _coord(request.GET.get("lat"), Decimal("-90"), Decimal("90"))
        longitude = _coord(request.GET.get("lng"), Decimal("-180"), Decimal("180"))
    except Exception:
        latitude = longitude = None
    if latitude is None or longitude is None:
        return JsonResponse({"ok": False, "error": "Pin an exact delivery location first."}, status=400)

    county = request.GET.get("county", "").strip()
    town = request.GET.get("town", "").strip()
    mode = request.GET.get("delivery_mode", DeliveryTariff.MODE_STANDARD).strip().lower() or DeliveryTariff.MODE_STANDARD
    cart = request.session.get("cart", {})
    items = []
    from .models import Product
    for product_id, raw_quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            quantity = min(max(0, int(raw_quantity)), product.stock_quantity)
        except (Product.DoesNotExist, TypeError, ValueError):
            continue
        if quantity > 0:
            items.append((product, quantity))
    if not items:
        return JsonResponse({"ok": False, "error": "Your cart is empty."}, status=400)

    try:
        quote = calculate_order_quote(items, latitude, longitude, county, town, mode)
    except ValueError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)

    return JsonResponse({
        "ok": True,
        "subtotal": f"{quote['subtotal']:.2f}",
        "commission": f"{quote['commission']:.2f}",
        "delivery_fee": f"{quote['delivery_fee']:.2f}",
        "total": f"{quote['total']:.2f}",
        "distance_km": f"{quote['distance_km']:.2f}",
        "distance_source": quote["distance_source"],
        "seller_count": quote["seller_count"],
        "county": quote["county"],
        "destination": quote["destination"],
        "delivery_mode": quote["delivery_mode"],
        "tariff_fee_per_seller": f"{quote['tariff_fee_per_seller']:.2f}",
        "tariff": tariff_text(),
    })

def checkout_mpesa_map(request):
    if request.method == "GET":
        cart = request.session.get("cart", {})
        items, total = [], Decimal("0.00")
        from .models import Product
        for product_id, raw_quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id, is_active=True)
                quantity = min(max(0, int(raw_quantity)), product.stock_quantity)
            except (Product.DoesNotExist, TypeError, ValueError):
                continue
            if quantity > 0:
                subtotal = product.discounted_price * quantity
                total += subtotal
                items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
        saved_addresses = []
        user = request.user
        if user.is_authenticated and not user.is_staff and not user.is_superuser:
            from .models import CustomerAddress
            saved_addresses = CustomerAddress.objects.filter(user=user).order_by("-is_default", "-created_at")[:8]
        return render(
            request,
            "customer_checkout_map.html",
            {"items": items, "total": total, "saved_addresses": saved_addresses},
        )

    latitude = _coord(request.POST.get("delivery_latitude"), Decimal("-90"), Decimal("90"))
    longitude = _coord(request.POST.get("delivery_longitude"), Decimal("-180"), Decimal("180"))
    if latitude is None or longitude is None:
        messages.error(request, "Select the exact delivery location on the map before continuing to payment.")
        return checkout_mpesa_map(_MapGetRequest(request))

    response = original_checkout_mpesa(request)
    match = re.search(r"/(?:order-success|payments/mpesa/waiting)/(\d+)/", getattr(response, "url", ""))
    if match:
        order_id = int(match.group(1))
        updates = {"delivery_latitude": latitude, "delivery_longitude": longitude}
        if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser:
            Order.objects.filter(pk=order_id, customer=request.user).update(**updates)
        else:
            Order.objects.filter(pk=order_id, email__iexact=request.POST.get("email", "").strip()).update(**updates)
    return response


class _MapGetRequest:
    def __init__(self, request):
        self.session = request.session
        self.user = request.user
        self.POST = {}
        self.FILES = {}
        self.META = request.META
        self.COOKIES = request.COOKIES
    method = "GET"
