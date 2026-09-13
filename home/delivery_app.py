from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
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
                agent.status = "available"
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

    order = get_object_or_404(Order.objects.select_for_update(), id=order_id, delivery_agent=agent)
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
    if order.status not in allowed[action]:
        return JsonResponse({"ok": False, "error": f"Order cannot be marked {target_status.replace('_', ' ')} from its current status."}, status=409)

    with transaction.atomic():
        order.status = target_status
        if target_status == "out_for_delivery":
            order.assigned_at = order.assigned_at or timezone.now()
        order.save(update_fields=["status", "assigned_at"] if target_status == "out_for_delivery" else ["status"])
        OrderEvent.objects.create(order=order, event_type=event_type, note=note, actor=request.user, delivery_agent=agent)
        if target_status == "delivered":
            agent.status = "available"
        else:
            agent.status = "on_delivery"
        agent.save(update_fields=["status"])

    return JsonResponse({"ok": True, "status": order.get_status_display(), "order_id": order.id})


@login_required(login_url="delivery_login")
def delivery_status(request):
    agent = _agent(request)
    if not agent:
        return JsonResponse({"ok": False, "error": "Delivery access is not active."}, status=403)

    orders = agent.orders.exclude(status__in=["delivered", "cancelled"]).select_related("delivery_agent").order_by("-created_at")
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
