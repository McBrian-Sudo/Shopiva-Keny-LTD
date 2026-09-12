from decimal import Decimal, InvalidOperation
import re

from .models import Order
from .payments import checkout_mpesa as original_checkout_mpesa


def _coord(value, low, high):
    try:
        value = Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError, AttributeError):
        return None
    return value.quantize(Decimal("0.000001")) if low <= value <= high else None


def checkout_mpesa_map(request):
    if request.method != "POST":
        return original_checkout_mpesa(request)
    latitude = _coord(request.POST.get("delivery_latitude"), Decimal("-90"), Decimal("90"))
    longitude = _coord(request.POST.get("delivery_longitude"), Decimal("-180"), Decimal("180"))
    if latitude is None or longitude is None:
        from django.contrib import messages
        messages.error(request, "Select the exact delivery location on the map before continuing to payment.")
        return original_checkout_mpesa(request)

    response = original_checkout_mpesa(request)
    url = getattr(response, "url", "")
    match = re.search(r"/(?:order-success|payments/mpesa/waiting)/(\d+)/", url)
    if match:
        Order.objects.filter(pk=int(match.group(1)), email__iexact=request.POST.get("email", "").strip()).update(
            delivery_latitude=latitude,
            delivery_longitude=longitude,
        )
    return response
