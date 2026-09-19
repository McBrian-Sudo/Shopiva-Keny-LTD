from decimal import Decimal, ROUND_UP
from math import asin, cos, radians, sin, sqrt
import json
import os
import urllib.error
import urllib.request


# Launch delivery tariff. Fees are based on estimated straight-line distance
# between the seller pickup point and the customer's pinned location.
# A road-routing provider can replace this calculator later without changing
# the order/pricing contract.
DISTANCE_BANDS = (
    (Decimal("3"), Decimal("150")),
    (Decimal("7"), Decimal("250")),
    (Decimal("12"), Decimal("350")),
    (Decimal("20"), Decimal("450")),
    (Decimal("30"), Decimal("550")),
    (Decimal("50"), Decimal("750")),
)

COMMISSION_LABEL = "Shopiva service fee"


def _decimal(value):
    return Decimal(str(value))


def haversine_km(lat1, lon1, lat2, lon2):
    """Return great-circle distance in kilometres."""
    lat1, lon1, lat2, lon2 = map(_decimal, (lat1, lon1, lat2, lon2))
    earth_radius_km = Decimal("6371.0088")

    phi1, phi2 = radians(float(lat1)), radians(float(lat2))
    dphi = radians(float(lat2 - lat1))
    dlambda = radians(float(lon2 - lon1))

    a = (
        sin(dphi / 2) ** 2
        + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    )
    return (
        earth_radius_km
        * Decimal(str(2 * asin(min(1.0, sqrt(a)))))
    ).quantize(Decimal("0.01"))


def _routes_api_distance_km(origin_lat, origin_lng, destination_lat, destination_lng):
    """Return Google road distance in km when a server-side Routes API key is configured."""
    api_key = (
        os.environ.get("GOOGLE_ROUTES_API_KEY", "").strip()
        or os.environ.get("GOOGLE_MAPS_SERVER_API_KEY", "").strip()
        or os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    )
    if not api_key:
        return None
    payload = {
        "origin": {"location": {"latLng": {"latitude": float(origin_lat), "longitude": float(origin_lng)}}},
        "destination": {"location": {"latLng": {"latitude": float(destination_lat), "longitude": float(destination_lng)}}},
        "travelMode": "DRIVE",
        "computeAlternativeRoutes": False,
        "languageCode": "en-US",
        "units": "METRIC",
    }
    req = urllib.request.Request(
        "https://routes.googleapis.com/directions/v2:computeRoutes",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "routes.distanceMeters,routes.duration",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as response:
            data = json.loads(response.read().decode("utf-8"))
        routes = data.get("routes") or []
        if not routes or routes[0].get("distanceMeters") is None:
            return None
        return (Decimal(str(routes[0]["distanceMeters"])) / Decimal("1000")).quantize(Decimal("0.01"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, KeyError, json.JSONDecodeError):
        return None


def delivery_fee_for_distance(distance_km):
    """Return the customer delivery fee for one seller-to-customer leg."""
    distance = max(Decimal("0"), _decimal(distance_km))
    for maximum_km, fee in DISTANCE_BANDS:
        if distance <= maximum_km:
            return fee

    extra_km = distance - Decimal("50")
    fee = Decimal("750") + (extra_km * Decimal("25"))
    # Bill whole KSh 10 blocks above 50km for predictable checkout amounts.
    return fee.quantize(Decimal("10"), rounding=ROUND_UP)


def calculate_order_quote(items, customer_latitude, customer_longitude):
    """
    Calculate:
      - item subtotal
      - value-based Shopiva commission
      - location-based delivery fee
      - total customer payment
    Delivery is charged once per unique seller represented in the cart.
    """
    from .commission import get_platform_commission_percent

    destination_lat = _decimal(customer_latitude)
    destination_lng = _decimal(customer_longitude)

    subtotal = Decimal("0.00")
    commission = Decimal("0.00")
    seller_legs = {}

    for product, quantity in items:
        quantity = int(quantity)
        unit_price = Decimal(product.discounted_price)
        gross = (unit_price * quantity).quantize(Decimal("0.01"))
        subtotal += gross

        rate = get_platform_commission_percent(unit_price)
        commission += (
            gross * rate / Decimal("100")
        ).quantize(Decimal("0.01"))

        seller = getattr(product, "seller", None)
        if not seller or not seller.is_active:
            raise ValueError(
                f"{product.name} cannot be ordered because its seller pickup location is unavailable."
            )

        lat = seller.business_latitude
        lng = seller.business_longitude
        if lat is None or lng is None:
            raise ValueError(
                f"{product.name} cannot be ordered until the seller adds a pickup location."
            )

        seller_legs.setdefault(
            seller.id,
            {
                "seller": seller,
                "latitude": _decimal(lat),
                "longitude": _decimal(lng),
            },
        )

    delivery_fee = Decimal("0.00")
    distances = []
    distance_sources = []

    for leg in seller_legs.values():
        road_distance = _routes_api_distance_km(
            leg["latitude"],
            leg["longitude"],
            destination_lat,
            destination_lng,
        )
        if road_distance is not None:
            distance = road_distance
            distance_sources.append("google_roads")
        else:
            distance = haversine_km(
                leg["latitude"],
                leg["longitude"],
                destination_lat,
                destination_lng,
            )
            distance_sources.append("estimated")
        fee = delivery_fee_for_distance(distance)
        distances.append(distance)
        delivery_fee += fee

    delivery_fee = delivery_fee.quantize(Decimal("0.01"))
    total = (subtotal + commission + delivery_fee).quantize(Decimal("0.01"))

    return {
        "subtotal": subtotal,
        "commission": commission.quantize(Decimal("0.01")),
        "delivery_fee": delivery_fee,
        "total": total,
        "distance_km": sum(distances, Decimal("0.00")).quantize(Decimal("0.01")),
        "seller_count": len(seller_legs),
        "distances": distances,
        "distance_source": "google_roads" if distance_sources and all(source == "google_roads" for source in distance_sources) else "estimated",
    }


def tariff_text():
    return (
        "0–3 km: KSh 150; 3–7 km: KSh 250; 7–12 km: KSh 350; "
        "12–20 km: KSh 450; 20–30 km: KSh 550; 30–50 km: KSh 750; "
        "50+ km: KSh 750 + KSh 25/km above 50 km."
    )
