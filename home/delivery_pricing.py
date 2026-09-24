from decimal import Decimal, ROUND_UP
from math import asin, cos, radians, sin, sqrt
import json
import os
import urllib.error
import urllib.request

from .models import DeliveryHub, DeliveryPricingProfile, DeliveryTariff

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
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_UNAWARE",
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


def _active_hub(customer_latitude=None, customer_longitude=None):
    hubs = list(DeliveryHub.objects.filter(is_active=True))
    if not hubs:
        return None
    if customer_latitude is None or customer_longitude is None:
        primary = next((hub for hub in hubs if hub.is_primary), None)
        return primary or hubs[0]

    # With multiple branches, choose the geographically nearest active hub.
    # Road distance is calculated after selection when the route is quoted.
    return min(
        hubs,
        key=lambda hub: float(haversine_km(
            hub.latitude, hub.longitude, customer_latitude, customer_longitude
        )),
    )


def _active_distance_profile(delivery_mode):
    profiles = list(
        DeliveryPricingProfile.objects.filter(
            is_active=True,
            delivery_mode=delivery_mode,
            pricing_mode=DeliveryPricingProfile.MODE_DISTANCE,
        ).order_by("-updated_at")
    )
    if len(profiles) > 1:
        raise ValueError("Shopiva has more than one active distance pricing profile for this delivery mode.")
    return profiles[0] if profiles else None


def _round_delivery_fee(value, step):
    step = _decimal(step)
    if step <= 0:
        return value.quantize(Decimal("0.01"))
    return (value / step).quantize(Decimal("1"), rounding=ROUND_UP) * step


def _distance_delivery_charge(profile, distance_km, seller_count, rural):
    charge = (
        profile.base_fee
        + (distance_km * profile.per_km_fee)
        + (max(0, seller_count - 1) * profile.per_seller_fee)
        + (profile.rural_surcharge if rural else Decimal("0.00"))
    )
    charge = max(charge, profile.minimum_fee)
    if profile.maximum_fee is not None:
        charge = min(charge, profile.maximum_fee)
    return _round_delivery_fee(charge, profile.rounding_step).quantize(Decimal("0.01"))


def calculate_order_quote(
    items,
    customer_latitude,
    customer_longitude,
    destination_county,
    destination_town,
    delivery_mode=DeliveryTariff.MODE_STANDARD,
):
    from .commission import get_platform_commission_percent

    destination_lat = _decimal(customer_latitude) if customer_latitude not in (None, "") else None
    destination_lng = _decimal(customer_longitude) if customer_longitude not in (None, "") else None

    # Coverage remains a separate concern from price. This prevents a rural
    # location from being rejected merely because it has no named tariff row.
    tariff, legacy_fee_per_seller = find_delivery_tariff(
        destination_county, destination_town, delivery_mode
    )

    subtotal = Decimal("0.00")
    commission = Decimal("0.00")
    seller_ids = set()
    for product, quantity in items:
        quantity = int(quantity)
        unit_price = Decimal(product.discounted_price)
        gross = (unit_price * quantity).quantize(Decimal("0.01"))
        subtotal += gross
        rate = get_platform_commission_percent(unit_price)
        commission += (gross * rate / Decimal("100")).quantize(Decimal("0.01"))
        seller = getattr(product, "seller", None)
        if not seller or not seller.is_active:
            raise ValueError(f"{product.name} cannot be ordered because its seller account is unavailable.")
        seller_ids.add(seller.id)

    seller_count = len(seller_ids)
    hub = _active_hub(destination_lat, destination_lng)
    distance = None
    distance_source = "not_pinned"
    if hub and destination_lat is not None and destination_lng is not None:
        distance = _routes_api_distance_km(
            hub.latitude, hub.longitude, destination_lat, destination_lng
        )
        if distance is not None:
            distance_source = "google_roads"
        else:
            distance = haversine_km(
                hub.latitude, hub.longitude, destination_lat, destination_lng
            )
            distance_source = "estimated"

    profile = _active_distance_profile(delivery_mode)
    if profile:
        if distance is None:
            raise ValueError(
                "Shopiva's distance-based delivery pricing requires an exact map pin. "
                "Please confirm your delivery location so the route from the active Shopiva hub can be calculated."
            )
        delivery_fee = _distance_delivery_charge(
            profile,
            distance,
            seller_count,
            tariff.is_fallback,
        )
        pricing_basis = "distance"
        base_fee = profile.base_fee
        distance_rate = profile.per_km_fee
        distance_charge = delivery_fee
        tariff_fee_per_seller = None
    else:
        delivery_fee = (legacy_fee_per_seller * seller_count).quantize(Decimal("0.01"))
        pricing_basis = "legacy_tariff"
        base_fee = Decimal("0.00")
        distance_rate = Decimal("0.00")
        distance_charge = Decimal("0.00")
        tariff_fee_per_seller = legacy_fee_per_seller

    total = (subtotal + commission + delivery_fee).quantize(Decimal("0.01"))
    return {
        "subtotal": subtotal,
        "commission": commission.quantize(Decimal("0.01")),
        "delivery_fee": delivery_fee,
        "total": total,
        "distance_km": distance,
        "seller_count": seller_count,
        "distances": [distance] if distance is not None else [],
        "distance_source": distance_source,
        "county": destination_county.strip(),
        "destination": destination_town.strip(),
        "tariff_destination": tariff.destination,
        "tariff_scope": "exact" if not tariff.is_fallback else "county_coverage",
        "delivery_mode": delivery_mode,
        "tariff_fee_per_seller": tariff_fee_per_seller,
        "hub": hub,
        "pricing_profile": profile,
        "pricing_basis": pricing_basis,
        "base_fee": base_fee,
        "distance_rate": distance_rate,
        "distance_charge": distance_charge,
    }


def tariff_text():
    if DeliveryPricingProfile.objects.filter(is_active=True, pricing_mode=DeliveryPricingProfile.MODE_DISTANCE).exists():
        return (
            "Shopiva delivery pricing is calculated from the active fulfillment hub "
            "to your exact delivery pin using the approved distance-pricing profile."
        )
    return (
        "Shopiva nationwide delivery coverage is active. Exact destination tariffs apply "
        "where configured; county-wide coverage applies to other towns and rural locations. "
        "Distance is calculated from the active Shopiva fulfillment hub for operational planning."
    )
