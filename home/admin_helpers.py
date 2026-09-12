from decimal import Decimal

from django.contrib.auth import logout
from django.db.models import Sum
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import DeliveryAgent, Order, PaymentTransaction, Product


def _require_admin(request):
    return bool(request.user.is_authenticated and request.user.is_staff)


@csrf_exempt
def admin_logout(request):
    """Reliable admin sign-out that does not fail on a stale CSRF token."""
    if request.method not in {"GET", "POST"}:
        return JsonResponse({"ok": False, "error": "Method not allowed."}, status=405)
    if not _require_admin(request):
        return HttpResponseRedirect(reverse("shopiva_admin:login"))
    logout(request)
    return HttpResponseRedirect(reverse("shopiva_admin:login"))


@csrf_exempt
def admin_ai_assistant(request):
    """Always-available admin operations assistant backed by live Shopiva data.

    The assistant remains useful even when an external LLM is unavailable and
    returns a normal JSON response instead of exposing provider errors to the UI.
    """
    if request.method != "POST":
        return JsonResponse({"ok": True, "answer": "Ask me about products, stock, orders, revenue, deliveries, or M-PESA."})
    if not _require_admin(request):
        return JsonResponse({"ok": False, "error": "Admin access required."}, status=403)

    question = request.POST.get("question", "").strip().lower()
    if not question:
        return JsonResponse({"ok": False, "error": "Please ask a question."}, status=400)

    products = Product.objects.all()
    orders = Order.objects.all()
    payments = PaymentTransaction.objects.all()
    riders = DeliveryAgent.objects.filter(is_active=True)

    if "low stock" in question or "low-stock" in question:
        rows = products.filter(is_active=True, stock_quantity__lte=5).order_by("stock_quantity", "name")[:10]
        answer = (
            "Low-stock products:\n" + "\n".join(f"• {p.name}: {p.stock_quantity} units" for p in rows)
            if rows else "There are currently no active products at or below 5 units of stock."
        )
    elif any(word in question for word in ("how many", "count", "total")) and "product" in question:
        answer = f"Shopiva currently has {products.count()} product(s), with {products.filter(is_active=True).count()} active."
    elif any(word in question for word in ("pending", "awaiting")) and "order" in question:
        answer = f"There are {orders.filter(status='pending').count()} pending order(s)."
    elif any(word in question for word in ("today", "today's")) and "order" in question:
        answer = f"Shopiva has received {orders.filter(created_at__date=timezone.localdate()).count()} order(s) today."
    elif any(word in question for word in ("revenue", "sales", "income")):
        revenue = orders.exclude(status="cancelled").aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")
        answer = f"Recorded revenue excluding cancelled orders is KSh {revenue:,.2f}."
    elif any(word in question for word in ("rider", "delivery", "agent")) and any(word in question for word in ("how many", "count", "online", "active")):
        online = riders.filter(status__in=("available", "on_delivery")).count()
        answer = f"Shopiva has {online} active delivery rider(s) currently marked available or on delivery."
    elif any(word in question for word in ("mpesa", "m-pesa", "payment")) and any(word in question for word in ("pending", "waiting")):
        pending = payments.filter(method="mpesa", status="pending").count()
        answer = f"There are {pending} M-PESA transaction(s) awaiting confirmed provider results. Pending does not mean paid."
    elif any(word in question for word in ("mpesa", "m-pesa", "payment")) and any(word in question for word in ("failed", "failure")):
        failed = payments.filter(method="mpesa", status="failed").count()
        answer = f"There are {failed} recorded failed M-PESA transaction(s)."
    elif "help" in question or "what can" in question:
        answer = "I can answer about products, low stock, orders, revenue, delivery riders, and M-PESA payment status."
    else:
        answer = "Try asking: How many products do we have? Which products are low stock? How many pending orders? What is our revenue? How many riders are active? Are any M-PESA payments pending?"

    return JsonResponse({"ok": True, "ai": False, "answer": answer})
