from decimal import Decimal
from math import asin, cos, radians, sin, sqrt
import json
import os
import urllib.error
import urllib.request

from .models import DeliveryTariff

COMMISSION_LABEL = "Shopiva service fee"

def _decimal(value):
    return Decimal(str(value))

def _normalize_location(value):
    return " ".join(str(value or "").strip().casefold().replace("-", " ").replace("/", " ").split())

def find_delivery_tariff(county, destination, mode=DeliveryTariff.MODE_STANDARD):
    county_text = str(county or "").strip()
    county_key = _normalize_location(county_text)
    destination_key = _normalize_location(destination)
    if mode not in {DeliveryTariff.MODE_STANDARD, DeliveryTariff.MODE_PICKUP, DeliveryTariff.MODE_EXPRESS}:
        raise ValueError("Invalid delivery option selected.")
    if not destination_key:
        raise ValueError("Select your delivery town or exact location before continuing.")

    qs = DeliveryTariff.objects.filter(is_active=True)
    exact = []
    if county_key:
        exact = [
            row for row in qs.filter(county__iexact=county_text, is_fallback=False)
            if _normalize_location(row.destination) == destination_key
        ]
    if not exact and not county_key:
        exact = [row for row in qs.filter(is_fallback=False) if _normalize_location(row.destination) == destination_key]
    if len(exact) > 1:
        raise ValueError("More than one delivery tariff matches this destination. Select the correct county.")
    if exact:
        tariff = exact[0]
        return tariff, tariff.fee_for_mode(mode)

    if county_key:
        fallback = [row for row in qs.filter(is_fallback=True) if _normalize_location(row.county) == county_key]
        if len(fallback) == 1:
            tariff = fallback[0]
            return tariff, tariff.fee_for_mode(mode)
        if len(fallback) > 1:
            raise ValueError("Shopiva has more than one county-wide delivery rule. Please contact support.")

    raise ValueError(
        f"Shopiva could not determine nationwide delivery coverage for '{county_text or destination}'. "
        "Search and select your exact Kenyan location so Shopiva can identify the correct county."
    )

def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(_decimal, (lat1, lon1, lat2, lon2))
    earth_radius_km = Decimal("6371.0088")
    phi1, phi2 = radians(float(lat1)), radians(float(lat2))
    dphi, dlambda = radians(float(lat2 - lat1)), radians(float(lon2 - lon1))
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return (earth_radius_km * Decimal(str(2 * asin(min(1.0, sqrt(a)))))).quantize(Decimal("0.01"))

def _routes_api_distance_km(origin_lat, origin_lng, destination_lat, destination_lng):
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
        "travelMode": "DRIVE", "computeAlternativeRoutes": False,
        "languageCode": "en-US", "units": "METRIC",
    }
    req = urllib.request.Request(
        "https://routes.googleapis.com/directions/v2:computeRoutes",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-Goog-Api-Key": api_key, "X-Goog-FieldMask": "routes.distanceMeters,routes.duration"},
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

def calculate_order_quote(items, customer_latitude, customer_longitude, destination_county, destination_town, delivery_mode=DeliveryTariff.MODE_STANDARD):
    from .commission import get_platform_commission_percent
    destination_lat = _decimal(customer_latitude) if customer_latitude not in (None, "") else None
    destination_lng = _decimal(customer_longitude) if customer_longitude not in (None, "") else None
    tariff, fee_per_seller = find_delivery_tariff(destination_county, destination_town, delivery_mode)
    subtotal = Decimal("0.00")
    commission = Decimal("0.00")
    seller_legs = {}
    for product, quantity in items:
        quantity = int(quantity)
        unit_price = Decimal(product.discounted_price)
        gross = (unit_price * quantity).quantize(Decimal("0.01"))
        subtotal += gross
        rate = get_platform_commission_percent(unit_price)
        commission += (gross * rate / Decimal("100")).quantize(Decimal("0.01"))
        seller = getattr(product, "seller", None)
        if not seller or not seller.is_active:
            raise ValueError(f"{product.name} cannot be ordered because its seller pickup location is unavailable.")
        if seller.business_latitude is None or seller.business_longitude is None:
            raise ValueError(f"{product.name} cannot be ordered until the seller adds a pickup location.")
        seller_legs.setdefault(seller.id, {"latitude": _decimal(seller.business_latitude), "longitude": _decimal(seller.business_longitude)})
    distances, distance_sources = [], []
    if destination_lat is not None and destination_lng is not None:
      for leg in seller_legs.values():
        road_distance = _routes_api_distance_km(leg["latitude"], leg["longitude"], destination_lat, destination_lng)
        if road_distance is not None:
            distance, source = road_distance, "google_roads"
        else:
            distance, source = haversine_km(leg["latitude"], leg["longitude"], destination_lat, destination_lng), "estimated"
        distances.append(distance)
        distance_sources.append(source)
    delivery_fee = (fee_per_seller * len(seller_legs)).quantize(Decimal("0.01"))
    total = (subtotal + commission + delivery_fee).quantize(Decimal("0.01"))
    return {
        "subtotal": subtotal, "commission": commission.quantize(Decimal("0.01")),
        "delivery_fee": delivery_fee, "total": total,
        "distance_km": sum(distances, Decimal("0.00")).quantize(Decimal("0.01")) if distances else None,
        "seller_count": len(seller_legs), "distances": distances,
        "distance_source": ("google_roads" if distance_sources and all(x == "google_roads" for x in distance_sources) else "estimated") if distances else "not_pinned",
        "county": tariff.county,
        "destination": destination_town.strip(),
        "tariff_destination": tariff.destination,
        "tariff_scope": "exact" if not tariff.is_fallback else "county_coverage",
        "delivery_mode": delivery_mode, "tariff_fee_per_seller": fee_per_seller,
    }

def tariff_text():
    return "Shopiva nationwide destination tariffs are active. Standard delivery is the default checkout mode."
