from decimal import Decimal

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from .models import DeliveryAgent, Order, PaymentTransaction, Product


def _require_admin(request):
    return bool(request.user.is_authenticated and request.user.is_staff)


def _no_store(response):
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


@never_cache
def admin_login(request):
    """Dedicated Shopiva admin login using Django's validated authentication form."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("shopiva_admin:index")

    form = AuthenticationForm(request, data=request.POST or None)
    next_url = request.POST.get("next") or request.GET.get("next") or ""

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if not user.is_active:
            form.add_error(None, "This administrator account is inactive.")
        elif not user.is_staff:
            form.add_error(None, "This account is not authorized for the Shopiva Control Center.")
        else:
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return HttpResponseRedirect(next_url)
            return redirect("shopiva_admin:index")

    context = {
        "form": form,
        "app_path": request.path,
        "next": next_url,
        "site_header": "Shopiva Control Center",
        "site_title": "Shopiva Admin",
    }
    return render(request, "admin/login.html", context)


@csrf_exempt
@never_cache
def admin_logout(request):
    """Destroy the admin session and explicitly prevent cached authenticated pages."""
    if request.method not in {"GET", "POST"}:
        return _no_store(JsonResponse({"ok": False, "error": "Method not allowed."}, status=405))
    if not _require_admin(request):
        return _no_store(HttpResponseRedirect(reverse("shopiva_admin:login")))
    logout(request)
    return _no_store(HttpResponseRedirect(reverse("shopiva_admin:login")))


@csrf_exempt
@never_cache
def admin_ai_assistant(request):
    """Nia Operations Copilot: role-scoped, live-data grounded admin assistance."""
    if request.method != "POST":
        return JsonResponse({
            "ok": True,
            "answer": "I'm Nia, your Shopiva Operations Copilot. Ask me about orders, payments, delivery, staff approvals, stock or revenue.",
        })
    if not _require_admin(request):
        return JsonResponse({"ok": False, "error": "Admin access required."}, status=403)

    question = request.POST.get("question", "").strip()
    if not question:
        return JsonResponse({"ok": False, "error": "Please ask Nia a question."}, status=400)
    lowered = question.lower()

    products = Product.objects.all()
    orders = Order.objects.all()
    payments = PaymentTransaction.objects.all()
    riders = DeliveryAgent.objects.filter(is_active=True)

    if "low stock" in lowered or "low-stock" in lowered:
        rows = products.filter(is_active=True, stock_quantity__lte=5).order_by("stock_quantity", "name")[:10]
        fallback = (
            "Low-stock products:\n" + "\n".join(f"• {p.name}: {p.stock_quantity} units" for p in rows)
            if rows else "There are currently no active products at or below 5 units of stock."
        )
    elif any(word in lowered for word in ("pending", "awaiting")) and "order" in lowered:
        fallback = f"There are {orders.filter(status='pending').count()} pending order(s)."
    elif any(word in lowered for word in ("today", "today's")) and "order" in lowered:
        fallback = f"Shopiva has received {orders.filter(created_at__date=timezone.localdate()).count()} order(s) today."
    elif any(word in lowered for word in ("revenue", "sales", "income")):
        revenue = orders.exclude(status="cancelled").aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")
        fallback = f"Recorded revenue excluding cancelled orders is KSh {revenue:,.2f}."
    elif any(word in lowered for word in ("rider", "delivery", "agent")) and any(word in lowered for word in ("how many", "count", "online", "active")):
        online = riders.filter(status__in=("available", "on_delivery")).count()
        fallback = f"Shopiva has {online} active delivery rider(s) currently marked available or on delivery."
    elif any(word in lowered for word in ("mpesa", "m-pesa", "payment")) and any(word in lowered for word in ("pending", "waiting")):
        pending = payments.filter(method="mpesa", status="pending").count()
        fallback = f"There are {pending} M-PESA transaction(s) awaiting confirmed provider results. Pending does not mean paid."
    elif any(word in lowered for word in ("mpesa", "m-pesa", "payment")) and any(word in lowered for word in ("failed", "failure")):
        failed = payments.filter(method="mpesa", status="failed").count()
        fallback = f"There are {failed} recorded failed M-PESA transaction(s)."
    elif any(word in lowered for word in ("staff", "approval", "approvals")):
        pending_staff = DeliveryAgent.objects.filter(is_active=False).count()
        fallback = f"There are {pending_staff} inactive delivery-agent account(s) requiring review. Use the Staff Approval Center before activating access."
    elif any(word in lowered for word in ("help", "what can")):
        fallback = "I can help with orders, payments, delivery, staff approvals, inventory and revenue."
    else:
        fallback = "Try: “How many pending orders?”, “Which products are low stock?”, “Are any M-PESA payments pending?”, or “How many staff approvals are waiting?”"

    import json
    import os
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return JsonResponse({"ok": True, "ai": False, "answer": fallback})

    snapshot = {
        "products_total": products.count(),
        "active_products": products.filter(is_active=True).count(),
        "low_stock": list(products.filter(is_active=True, stock_quantity__lte=5).order_by("stock_quantity", "name").values("id", "name", "stock_quantity")[:20]),
        "orders_pending": orders.filter(status="pending").count(),
        "orders_today": orders.filter(created_at__date=timezone.localdate()).count(),
        "revenue_excluding_cancelled": str(orders.exclude(status="cancelled").aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")),
        "mpesa_pending": payments.filter(method="mpesa", status="pending").count(),
        "mpesa_failed": payments.filter(method="mpesa", status="failed").count(),
        "active_riders": riders.filter(status__in=("available", "on_delivery")).count(),
        "inactive_delivery_accounts": DeliveryAgent.objects.filter(is_active=False).count(),
    }
    prompt = f"""
You are Nia, Shopiva Kenya's Operations Copilot for an authenticated administrator.
Answer using only the supplied live Shopiva snapshot.
You may explain operations and direct the administrator to the correct control center.
Never invent figures, payment results, staff decisions, customer data, or system state.
Do not claim that you changed data. The current Nia chat is read-only.
Keep answers concise and practical. Use KSh when discussing money.
LIVE SHOPIVA SNAPSHOT:
{json.dumps(snapshot, default=str, ensure_ascii=False)}
ADMIN QUESTION:
{question}
"""
    try:
        from openai import OpenAI
        response = OpenAI(api_key=api_key).responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
            input=prompt,
        )
        answer = response.output_text.strip() or fallback
        return JsonResponse({"ok": True, "ai": True, "answer": answer})
    except Exception:
        return JsonResponse({"ok": True, "ai": False, "answer": fallback})

