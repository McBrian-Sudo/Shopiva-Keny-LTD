from decimal import Decimal, InvalidOperation
from datetime import timedelta
import secrets

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import DeliveryAgent, DeliveryLocationPing, Order, OrderEvent, SellerSettlement, SellerWallet
from .notification_service import notify_user
from .forms import DeliveryRegistrationForm


DELIVERY_CODE_MAX_ATTEMPTS = 5
DELIVERY_CODE_LOCK_MINUTES = 10


def _agent(request):
    try:
        agent = request.user.delivery_agent_profile
    except DeliveryAgent.DoesNotExist:
        return None
    return agent if agent.is_active else None


def _release_seller_settlements(order, now):
    released = []
    for settlement in SellerSettlement.objects.select_for_update().filter(order=order, status="pending"):
        wallet, _ = SellerWallet.objects.get_or_create(seller=settlement.seller)
        wallet = SellerWallet.objects.select_for_update().get(pk=wallet.pk)
        wallet.pending_balance = max(Decimal("0.00"), wallet.pending_balance - settlement.seller_amount)
        wallet.available_balance += settlement.seller_amount
        wallet.save(update_fields=("pending_balance", "available_balance", "updated_at"))
        settlement.status = "available"
        settlement.released_at = now
        settlement.save(update_fields=("status", "released_at"))
           released.append(settlement)
    return released


def delivery_signup(request):
    """Create a delivery-partner application; staff approval is required before deliveries are accessible."""
    if request.user.is_authenticated:
        if _agent(request):
            return redirect("delivery_portal")
        if request.user.is_staff or request.user.is_superuser:
            return redirect("/admin/")

    if request.method == "POST":
        form = DeliveryRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
            except IntegrityError:
                form.add_error("username", "This account could not be created because the username or email already exists.")
            else:
                return render(request, "delivery/signup_success.html", {"username": user.username, "email": user.email})
    else:
        form = DeliveryRegistrationForm()

    return render(request, "delivery/signup.html", {"form": form})


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
                form.add_error(None, "Your staff application is registered and awaiting administrator verification.")
            else:
                login(request, agent.user)
                agent.status = "on_delivery" if agent.orders.filter(status="out_for_delivery").exists() else "available"
                agent.save(update_fields=["status"])
                return redirect("delivery_portal")

    return render(request, "delivery/login.html", {"form": form})

@login_required(login_url="delivery_login")
def delivery_logout(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    agent = _agent(request)
    if agent:
        agent.status = "offline"
        agent.save(update_fields=["status"])
    logout(request)
    return redirect("delivery_login")
