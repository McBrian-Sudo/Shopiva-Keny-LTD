from decimal import Decimal, InvalidOperation
import re

from django.contrib import messages
from django.shortcuts import render

from .models import Order
from .payments import checkout_mpesa as original_checkout_mpesa


def _coord(value, low, high):
    try:
        value = Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError, AttributeError):
        return None
    return value.quantize(Decimal("0.000001")) if low <= value <= high else None


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
        return render(request, "checkout_map.html", {"items": items, "total": total})

    latitude = _coord(request.POST.get("delivery_latitude"), Decimal("-90"), Decimal("90"))
    longitude = _coord(request.POST.get("delivery_longitude"), Decimal("-180"), Decimal("180"))
    if latitude is None or longitude is None:
        messages.error(request, "Select the exact delivery location on the map before continuing to payment.")
        return checkout_mpesa_map(_MapGetRequest(request))

    response = original_checkout_mpesa(request)
    match = re.search(r"/(?:order-success|payments/mpesa/waiting)/(\d+)/", getattr(response, "url", ""))
    if match:
        Order.objects.filter(pk=int(match.group(1)), email__iexact=request.POST.get("email", "").strip()).update(
            delivery_latitude=latitude, delivery_longitude=longitude
        )
    return response


class _MapGetRequest:
    def __init__(self, request):
        self.session = request.session
    method = "GET"
