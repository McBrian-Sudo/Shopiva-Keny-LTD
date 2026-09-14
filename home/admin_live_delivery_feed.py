from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils import timezone

from .models import DeliveryAgent


ACTIVE_STATUSES = {
    "confirmed",
    "paid",
    "packed",
    "processing",
    "shipped",
    "out_for_delivery",
}


@staff_member_required(login_url="admin_login")
def admin_live_delivery_feed(request):
    """Protected live delivery feed for the Shopiva operations/admin app."""
    agents = DeliveryAgent.objects.filter(is_active=True).select_related("user")
    payload = []
    now = timezone.now()

    for agent in agents:
        latest_order = (
            agent.orders
            .filter(status__in=ACTIVE_STATUSES)
            .order_by("-created_at")
            .first()
        )
        latest_ping = agent.location_history.order_by("-recorded_at").first()
        latitude = float(agent.current_latitude) if agent.current_latitude is not None else None
        longitude = float(agent.current_longitude) if agent.current_longitude is not None else None

        stale_seconds = None
        if agent.last_location_at:
            stale_seconds = max(0, int((now - agent.last_location_at).total_seconds()))

        destination_latitude = None
        destination_longitude = None
        if latest_order:
            destination_latitude = (
                float(latest_order.delivery_latitude)
                if latest_order.delivery_latitude is not None
                else None
            )
            destination_longitude = (
                float(latest_order.delivery_longitude)
                if latest_order.delivery_longitude is not None
                else None
            )

        payload.append(
            {
                "id": agent.id,
                "name": agent.display_name,
                "phone": agent.phone or "",
                "vehicle_type": agent.vehicle_type or "",
                "vehicle_number": agent.vehicle_number or "",
                "status": agent.get_status_display(),
                "status_code": agent.status,
                "live": agent.location_is_live,
                "latitude": latitude,
                "longitude": longitude,
                "updated": agent.last_location_at.isoformat() if agent.last_location_at else None,
                "stale_seconds": stale_seconds,
                "accuracy": float(latest_ping.accuracy_meters) if latest_ping and latest_ping.accuracy_meters is not None else None,
                "speed_mps": float(latest_ping.speed_mps) if latest_ping and latest_ping.speed_mps is not None else 0,
                "heading": float(latest_ping.heading_degrees) if latest_ping and latest_ping.heading_degrees is not None else None,
                "order": {
                    "id": latest_order.id if latest_order else None,
                    "tracking_code": latest_order.tracking_code if latest_order else "",
                    "status": latest_order.get_status_display() if latest_order else "No active order",
                    "address": latest_order.address if latest_order else "",
                    "destination_latitude": destination_latitude,
                    "destination_longitude": destination_longitude,
                },
            }
        )

    return JsonResponse({
        "ok": True,
        "updated_at": now.isoformat(),
        "server_time": now.isoformat(),
        "agents": payload,
    })
