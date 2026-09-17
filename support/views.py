from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from home.models import Notification, SellerProfile

from .models import SupportMessage, SupportTicket

User = get_user_model()


def _role_for(user):
    if user.is_staff or user.is_superuser:
        return "staff"
    if SellerProfile.objects.filter(user=user, is_active=True).exists():
        return "seller"
    return "customer"


def _staff_notify(title, body, link):
    staff_users = User.objects.filter(is_staff=True, is_active=True)
    Notification.objects.bulk_create(
        [
            Notification(
                user=staff_user,
                notification_type="system",
                title=title[:160],
                message=body,
                link=link[:255],
            )
            for staff_user in staff_users
        ]
    )


def _user_notify(user, title, body, link):
    Notification.objects.create(
        user=user,
        notification_type="system",
        title=title[:160],
        message=body,
        link=link[:255],
    )


def _messages_payload(ticket):
    return [
        {
            "id": message.id,
            "body": message.body,
            "from_staff": message.from_staff,
            "author": "Shopiva Support" if message.from_staff else (message.author.get_full_name() or message.author.username if message.author else "You"),
            "created_at": message.created_at.isoformat(),
        }
        for message in ticket.messages.select_related("author").all()
    ]


@login_required(login_url="customer_login")
def support_center(request):
    role = _role_for(request.user)
    if role == "staff":
        return redirect("support_admin_center")

    role_label = "Seller" if role == "seller" else "Customer"
    back_url = "seller_dashboard" if role == "seller" else "customer_dashboard"
    tickets = SupportTicket.objects.filter(user=request.user).prefetch_related("messages__author")

    selected_id = request.GET.get("ticket") or request.POST.get("ticket_id")
    selected_ticket = None
    if selected_id:
        selected_ticket = get_object_or_404(tickets, id=selected_id)

    if request.method == "GET" and request.GET.get("format") == "json" and selected_ticket:
        return JsonResponse(
            {
                "ok": True,
                "status": selected_ticket.status,
                "status_label": selected_ticket.get_status_display(),
                "messages": _messages_payload(selected_ticket),
            }
        )

    if request.method == "POST":
        action = request.POST.get("action", "")
        if action == "new":
            subject = request.POST.get("subject", "").strip()
            body = request.POST.get("body", "").strip()
            category = request.POST.get("category", "General").strip() or "General"
            priority = request.POST.get("priority", "normal")
            order_reference = request.POST.get("order_reference", "").strip()
            allowed_priorities = {choice[0] for choice in SupportTicket.PRIORITY_CHOICES}
            if not subject or len(subject) < 4 or not body:
                messages.error(request, "Please provide a subject and describe the issue so our support team can help.")
            elif priority not in allowed_priorities:
                messages.error(request, "Please select a valid support priority.")
            else:
                with transaction.atomic():
                    ticket = SupportTicket.objects.create(
                        user=request.user,
                        role=role,
                        subject=subject[:160],
                        category=category[:80],
                        priority=priority,
                        order_reference=order_reference[:120],
                        last_response_at=timezone.now(),
                    )
                    SupportMessage.objects.create(ticket=ticket, author=request.user, body=body[:8000], from_staff=False)
                    transaction.on_commit(
                        lambda: _staff_notify(
                            f"New {role_label.lower()} support case",
                            f"{role_label} {request.user.username} opened '{ticket.subject}'.",
                            f"/admin/support-center/?ticket={ticket.id}",
                        )
                    )
                messages.success(request, f"Support case {str(ticket.id)[:8].upper()} opened. Our support desk has the case.")
                return redirect(f"/support/?ticket={ticket.id}")

        elif action == "reply" and selected_ticket:
            body = request.POST.get("body", "").strip()
            if body:
                SupportMessage.objects.create(ticket=selected_ticket, author=request.user, body=body[:8000], from_staff=False)
                selected_ticket.status = "open"
                selected_ticket.last_response_at = timezone.now()
                selected_ticket.save(update_fields=["status", "last_response_at", "updated_at"])
                _staff_notify(
                    f"Customer replied to support case" if role == "customer" else "Seller replied to support case",
                    f"{role_label} {request.user.username} replied to '{selected_ticket.subject}'.",
                    f"/admin/support-center/?ticket={selected_ticket.id}",
                )
                messages.success(request, "Your reply has been sent to Shopiva Support.")
            return redirect(f"/support/?ticket={selected_ticket.id}")

    if selected_ticket is None:
        selected_ticket = tickets.first()

    return render(
        request,
        "support/center.html",
        {
            "tickets": tickets,
            "selected_ticket": selected_ticket,
            "role": role,
            "role_label": role_label,
            "back_url": back_url,
            "is_empty": not tickets.exists(),
        },
    )


@staff_member_required(login_url="admin_login")
def support_admin_center(request):
    tickets = SupportTicket.objects.select_related("user").prefetch_related("messages__author").all()

    status_filter = request.GET.get("status", "").strip()
    role_filter = request.GET.get("role", "").strip()
    priority_filter = request.GET.get("priority", "").strip()
    search = request.GET.get("q", "").strip()
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if role_filter:
        tickets = tickets.filter(role=role_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    if search:
        tickets = tickets.filter(Q(subject__icontains=search) | Q(category__icontains=search) | Q(order_reference__icontains=search) | Q(user__username__icontains=search))

    selected_id = request.GET.get("ticket") or request.POST.get("ticket_id")
    selected_ticket = get_object_or_404(SupportTicket.objects.select_related("user").prefetch_related("messages__author"), id=selected_id) if selected_id else tickets.first()

    if request.method == "GET" and request.GET.get("format") == "json" and selected_ticket:
        return JsonResponse(
            {
                "ok": True,
                "status": selected_ticket.status,
                "status_label": selected_ticket.get_status_display(),
                "messages": _messages_payload(selected_ticket),
            }
        )

    if request.method == "POST" and selected_ticket:
        action = request.POST.get("action", "")
        if action == "reply":
            body = request.POST.get("body", "").strip()
            if body:
                SupportMessage.objects.create(ticket=selected_ticket, author=request.user, body=body[:8000], from_staff=True)
                selected_ticket.status = "waiting_for_customer"
                selected_ticket.last_response_at = timezone.now()
                selected_ticket.save(update_fields=["status", "last_response_at", "updated_at"])
                _user_notify(
                    selected_ticket.user,
                    "Shopiva Support replied",
                    f"Support has replied to your case: {selected_ticket.subject}.",
                    f"/support/?ticket={selected_ticket.id}",
                )
                messages.success(request, "Reply sent to the customer/seller.")
        elif action == "status":
            new_status = request.POST.get("status", "")
            allowed = {choice[0] for choice in SupportTicket.STATUS_CHOICES}
            if new_status in allowed:
                selected_ticket.status = new_status
                selected_ticket.last_response_at = timezone.now()
                selected_ticket.save(update_fields=["status", "last_response_at", "updated_at"])
                _user_notify(
                    selected_ticket.user,
                    f"Support case {selected_ticket.get_status_display().lower()}",
                    f"Your Shopiva support case '{selected_ticket.subject}' is now {selected_ticket.get_status_display().lower()}.",
                    f"/support/?ticket={selected_ticket.id}",
                )
                messages.success(request, "Support case status updated.")
        return redirect(f"/admin/support-center/?ticket={selected_ticket.id}")

    open_count = SupportTicket.objects.filter(status__in=("open", "in_progress", "waiting_for_customer")).count()
    urgent_count = SupportTicket.objects.filter(priority="urgent", status__in=("open", "in_progress", "waiting_for_customer")).count()
    seller_count = SupportTicket.objects.filter(role="seller", status__in=("open", "in_progress", "waiting_for_customer")).count()

    return render(
        request,
        "support/admin_center.html",
        {
            "tickets": tickets,
            "selected_ticket": selected_ticket,
            "open_count": open_count,
            "urgent_count": urgent_count,
            "seller_count": seller_count,
            "status_choices": SupportTicket.STATUS_CHOICES,
            "role_choices": SupportTicket.ROLE_CHOICES,
            "priority_choices": SupportTicket.PRIORITY_CHOICES,
            "current_status": status_filter,
            "current_role": role_filter,
            "current_priority": priority_filter,
            "query": search,
        },
    )
