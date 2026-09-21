from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import DeliveryAgent, Notification, Order, PaymentTransaction, Product
from support.models import SupportTicket


SYSTEM_TICKET_Q = (
    Q(subject__startswith="Payment assistance for order")
    | Q(subject__startswith="Order cancellation assistance")
    | Q(subject__startswith="Cancelled order assistance")
)


@staff_member_required(login_url="admin_login")
def admin_operations_center(request):
    if request.method == "POST":
        action = request.POST.get("action", "").strip()
        agent_id = request.POST.get("agent_id", "").strip()
        if action in {"approve_delivery", "deactivate_delivery"} and agent_id.isdigit():
            agent = DeliveryAgent.objects.select_related("user").filter(id=int(agent_id)).first()
            if agent:
                enabled = action == "approve_delivery"
                agent.is_active = enabled
                if not enabled:
                    agent.status = "offline"
                agent.save(update_fields=["is_active", "status"])
                agent.user.is_active = enabled
                agent.user.save(update_fields=["is_active"])
                messages.success(
                    request,
                    f"{agent.display_name} is now {'approved for delivery operations' if enabled else 'deactivated from delivery operations'}.",
                )
            else:
                messages.error(request, "Delivery partner was not found.")
        return redirect("shopiva_admin:operations_center")

    active_statuses = ("open", "in_progress", "waiting_for_customer")
    pending_delivery = (
        DeliveryAgent.objects.filter(is_active=False)
        .select_related("user")
        .order_by("-created_at")[:50]
    )
    user_issues = SupportTicket.objects.exclude(SYSTEM_TICKET_Q).filter(
        status__in=active_statuses
    ).select_related("user").order_by("-updated_at")[:50]
    system_issues = SupportTicket.objects.filter(
        SYSTEM_TICKET_Q, status__in=active_statuses
    ).select_related("user").order_by("-updated_at")[:50]
    notifications = Notification.objects.select_related("user").order_by(
        "-created_at"
    )[:50]

    failed_payments = PaymentTransaction.objects.filter(
        status__in=("failed", "cancelled", "refunded")
    ).select_related("order").order_by("-updated_at")[:25]
    unassigned_orders = Order.objects.filter(
        delivery_agent__isnull=True,
        status__in=("confirmed", "paid", "packed", "processing", "shipped"),
    ).order_by("-created_at")[:25]
    low_stock = Product.objects.filter(
        is_active=True, stock_quantity__lte=5
    ).order_by("stock_quantity", "name")[:25]

    now = timezone.now()
    stale_riders = []
    for rider in DeliveryAgent.objects.filter(is_active=True).select_related("user"):
        if rider.last_location_at and (now - rider.last_location_at).total_seconds() > 90:
            stale_riders.append(rider)
        elif rider.status in {"available", "on_delivery"} and not rider.last_location_at:
            stale_riders.append(rider)

    return render(
        request,
        "admin/operations_center.html",
        {
            "pending_delivery": pending_delivery,
            "user_issues": user_issues,
            "system_issues": system_issues,
            "notifications": notifications,
            "failed_payments": failed_payments,
            "unassigned_orders": unassigned_orders,
            "low_stock": low_stock,
            "stale_riders": stale_riders[:25],
            "counts": {
                "pending_delivery": pending_delivery.count(),
                "user_issues": SupportTicket.objects.exclude(SYSTEM_TICKET_Q).filter(status__in=active_statuses).count(),
                "system_issues": SupportTicket.objects.filter(SYSTEM_TICKET_Q, status__in=active_statuses).count(),
                "unread_notifications": Notification.objects.filter(is_read=False).count(),
                "failed_payments": PaymentTransaction.objects.filter(status__in=("failed", "cancelled", "refunded")).count(),
                "unassigned_orders": Order.objects.filter(delivery_agent__isnull=True, status__in=("confirmed", "paid", "packed", "processing", "shipped")).count(),
                "low_stock": Product.objects.filter(is_active=True, stock_quantity__lte=5).count(),
                "stale_riders": len(stale_riders),
            },
        },
    )
