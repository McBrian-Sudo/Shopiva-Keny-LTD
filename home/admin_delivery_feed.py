from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils import timezone

from .models import DeliveryAgent


@staff_member_required(login_url="admin_login")
def admin_live_delivery_feed(request):
    """Return the protected live delivery network feed for Shopiva operations."""
    county = request.GET.get("county", "").strip().lower()
    agents = DeliveryAgent.objects.filter(is_active=True).select_related("user")
    now = timezone.now()
    payload = []

    for agent in agents:
        latest_order = (
            agent.orders
            .select_related("delivery_agent")
            .exclude(status="cancelled")
            .order_by("-created_at")
            .first()
        )
        order_address = latest_order.address if latest_order else ""
        if county and county not in (order_address or "").lower():
            continue

        latest_ping = agent.location_history.order_by("-recorded_at").first()
        updated = agent.last_location_at
        age_seconds = (now - updated).total_seconds() if updated else None
        live = bool(updated and age_seconds is not None and age_seconds <= 90)

        payload.append(
            {
                "id": agent.id,
                "name": agent.display_name,
                "phone": agent.phone or "",
                "vehicle_type": agent.vehicle_type or "",
                "vehicle_number": agent.vehicle_number or "",
                "status": agent.get_status_display(),
                "status_code": agent.status,
                "live": live,
                "latitude": float(agent.current_latitude) if agent.current_latitude is not None else None,
                "longitude": float(agent.current_longitude) if agent.current_longitude is not None else None,
                "updated": updated.isoformat() if updated else None,
                "accuracy": float(latest_ping.accuracy_meters) if latest_ping and latest_ping.accuracy_meters is not None else None,
                "speed_mps": float(latest_ping.speed_mps) if latest_ping and latest_ping.speed_mps is not None else 0,
                "heading": float(latest_ping.heading_degrees) if latest_ping and latest_ping.heading_degrees is not None else None,
                "order_id": latest_order.id if latest_order else None,
                "tracking_code": latest_order.tracking_code if latest_order else "",
                "order_status": latest_order.get_status_display() if latest_order else "No active order",
                "order_raw_status": latest_order.status if latest_order else "",
                "destination": order_address,
                "destination_latitude": float(latest_order.delivery_latitude) if latest_order and latest_order.delivery_latitude is not None else None,
                "destination_longitude": float(latest_order.delivery_longitude) if latest_order and latest_order.delivery_longitude is not None else None,
            }
        )

    return JsonResponse(
        {
            "ok": True,
            "updated_at": now.isoformat(),
            "agents": payload,
            "refresh_seconds": 5,
        },
        headers={"Cache-Control": "no-store, max-age=0"},
    )
