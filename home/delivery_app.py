from decimal import Decimal, InvalidOperation

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import DeliveryAgent, DeliveryLocationPing, Order, OrderEvent


def _agent(request):
    try:
        agent = request.user.delivery_agent_profile
    except DeliveryAgent.DoesNotExist:
        return None
    return agent if agent.is_active else None


def delivery_login(request):
    if request.user.is_authenticated:
        if _agent(request):
            return redirect("delivery_portal")
        if request.user.is_staff or request.user.is_superuser:
            return redirect("/admin/")
        logout(request)

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        try:
            agent = user.delivery_agent_profile
        except DeliveryAgent.DoesNotExist:
            form.add_error(None, "This account is not registered as a Shopiva delivery partner.")
        else:
            if not agent.is_active:
                form.add_error(None, "Your delivery partner account is inactive.")
            else:
                login(request, user)
                agent.status = "on_delivery" if agent.orders.filter(status="out_for_delivery").exists() else "available"
                agent.save(update_fields=["status"])
                return redirect("delivery_portal")

    return render(request, "delivery/login.html", {"form": form})


@login_required(login_url="delivery_login")
def delivery_logout(request):
    agent = _agent(request)
    if agent:
        agent.status = "offline"
        agent.save(update_fields=["status"])
    logout(request)
    return redirect("delivery_login")


@login_required(login_url="delivery_login")
def delivery_action(request, order_id):
    agent = _agent(request)
    if not agent:
        return JsonResponse({"ok": False, "error": "Delivery access is not active."}, status=403)
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    action = request.POST.get("action", "").strip().lower()
    transitions = {
        "start": ("out_for_delivery", "out_for_delivery", "Delivery partner started the delivery."),
        "delivered": ("delivered", "delivered", "Delivery partner marked the order delivered."),
    }
    transition = transitions.get(action)
    if not transition:
        return JsonResponse({"ok": False, "error": "Unknown delivery action."}, status=400)

    target_status, event_type, note = transition
    allowed = {
        "out_for_delivery": {"packed", "processing", "shipped", "confirmed", "paid"},
        "delivered": {"out_for_delivery"},
    }

    with transaction.atomic():
        try:
            order = Order.objects.select_for_update().get(id=order_id, delivery_agent=agent)
        except Order.DoesNotExist:
            return JsonResponse({"ok": False, "error": "Delivery order not found or not assigned to you."}, status=404)

        if order.status not in allowed[action]:
            return JsonResponse({
                "ok": False,
                "error": f"Order cannot be marked {target_status.replace('_', ' ')} from its current status.",
            }, status=409)

        order.status = target_status
        if target_status == "out_for_delivery":
            order.assigned_at = order.assigned_at or timezone.now()
        order.save(
            update_fields=["status", "assigned_at"]
            if target_status == "out_for_delivery"
            else ["status"]
        )
        OrderEvent.objects.create(
            order=order,
            event_type=event_type,
            note=note,
            actor=request.user,
            delivery_agent=agent,
        )
        agent.status = "available" if target_status == "delivered" else "on_delivery"
        agent.save(update_fields=["status"])

    return JsonResponse({
        "ok": True,
        "status": order.get_status_display(),
        "order_id": order.id,
    })


@login_required(login_url="delivery_login")
def delivery_status(request):
    agent = _agent(request)
    if not agent:
        return JsonResponse({"ok": False, "error": "Delivery access is not active."}, status=403)

    orders = (
        agent.orders
        .exclude(status__in=["delivered", "cancelled"])
        .select_related("delivery_agent")
        .order_by("-created_at")
    )
    return JsonResponse({
        "ok": True,
        "agent": {
            "id": agent.id,
            "name": agent.display_name,
            "status": agent.get_status_display(),
            "live": agent.location_is_live,
            "latitude": float(agent.current_latitude) if agent.current_latitude is not None else None,
            "longitude": float(agent.current_longitude) if agent.current_longitude is not None else None,
            "updated": agent.last_location_at.isoformat() if agent.last_location_at else None,
        },
        "orders": [{
            "id": order.id,
            "tracking_code": order.tracking_code,
            "customer_name": order.customer_name,
            "phone": order.phone,
            "address": order.address,
            "latitude": float(order.delivery_latitude) if order.delivery_latitude is not None else None,
            "longitude": float(order.delivery_longitude) if order.delivery_longitude is not None else None,
            "status": order.get_status_display(),
            "raw_status": order.status,
            "total": str(order.total_amount),
        } for order in orders],
    })


@login_required(login_url="delivery_login")
def delivery_update_location(request):
    if request.method != "POST":
        return redirect("delivery_portal")
    agent = _agent(request)
    if not agent:
        return redirect("/admin/")

    try:
        latitude = Decimal(request.POST.get("latitude", ""))
        longitude = Decimal(request.POST.get("longitude", ""))
    except (InvalidOperation, TypeError):
        return redirect("delivery_portal")

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return redirect("delivery_portal")

    now = timezone.now()
    agent.current_latitude = latitude.quantize(Decimal("0.000001"))
    agent.current_longitude = longitude.quantize(Decimal("0.000001"))
    agent.last_location_at = now
    agent.status = "on_delivery" if agent.orders.filter(status="out_for_delivery").exists() else "available"
    agent.save(update_fields=["current_latitude", "current_longitude", "last_location_at", "status"])
    DeliveryLocationPing.objects.create(
        agent=agent,
        latitude=agent.current_latitude,
        longitude=agent.current_longitude,
    )
    return redirect("delivery_portal")


@login_required(login_url="delivery_login")
def delivery_ping_location(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    agent = _agent(request)
    if not agent:
        return JsonResponse({"ok": False, "error": "Delivery partner access is not active."}, status=403)

    try:
        latitude = Decimal(str(request.POST.get("latitude", "")))
        longitude = Decimal(str(request.POST.get("longitude", "")))
    except (InvalidOperation, TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Invalid coordinates."}, status=400)

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return JsonResponse({"ok": False, "error": "Coordinates are out of range."}, status=400)

    latest_ping = agent.location_history.order_by("-recorded_at").first()
    if latest_ping and (timezone.now() - latest_ping.recorded_at).total_seconds() < 3:
        return JsonResponse({"ok": False, "error": "Location update rate limited. Please wait a moment."}, status=429)

    def optional_decimal(field_name, minimum=None, maximum=None):
        raw = request.POST.get(field_name, "").strip()
        if not raw:
            return None
        try:
            value = Decimal(raw)
        except (InvalidOperation, TypeError, ValueError):
            return None
        if minimum is not None and value < minimum:
            return None
        if maximum is not None and value > maximum:
            return None
        return value

    accuracy = optional_decimal("accuracy", minimum=Decimal("0"), maximum=Decimal("100000"))
    speed = optional_decimal("speed", minimum=Decimal("0"), maximum=Decimal("100"))
    heading = optional_decimal("heading", minimum=Decimal("0"), maximum=Decimal("360"))

    now = timezone.now()
    latitude = latitude.quantize(Decimal("0.000001"))
    longitude = longitude.quantize(Decimal("0.000001"))
    agent.current_latitude = latitude
    agent.current_longitude = longitude
    agent.last_location_at = now
    agent.status = "on_delivery" if agent.orders.filter(status="out_for_delivery").exists() else "available"
    agent.save(update_fields=["current_latitude", "current_longitude", "last_location_at", "status"])

    DeliveryLocationPing.objects.create(
        agent=agent,
        latitude=latitude,
        longitude=longitude,
        accuracy_meters=accuracy.quantize(Decimal("0.01")) if accuracy is not None else None,
        speed_mps=speed.quantize(Decimal("0.01")) if speed is not None else None,
        heading_degrees=heading.quantize(Decimal("0.01")) if heading is not None else None,
    )

    return JsonResponse({
        "ok": True,
        "updated_at": now.isoformat(),
        "latitude": float(latitude),
        "longitude": float(longitude),
        "status": agent.get_status_display(),
    })
