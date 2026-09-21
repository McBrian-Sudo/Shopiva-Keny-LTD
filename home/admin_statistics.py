from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from .models import DeliveryAgent, Order, Product, SellerProfile


@staff_member_required(login_url="/admin/login/")
def statistics_center(request):
    User = get_user_model()
    orders = Order.objects.all()
    products = Product.objects.all()
    customers = User.objects.filter(
        is_staff=False,
        is_superuser=False,
        seller_profile__isnull=True,
        delivery_agent_profile__isnull=True,
    )
    total_revenue = (
        orders.exclude(status="cancelled").aggregate(value=Sum("total_amount")).get("value")
        or Decimal("0.00")
    )

    today = timezone.localdate()
    start = today - timedelta(days=6)
    daily = []
    values = []
    for offset in range(7):
        day = start + timedelta(days=offset)
        value = (
            orders.filter(created_at__date=day)
            .exclude(status="cancelled")
            .aggregate(value=Sum("total_amount"))
            .get("value")
            or Decimal("0.00")
        )
        daily.append({"day": day, "label": day.strftime("%a"), "value": value})
        values.append(float(value))

    max_value = max(values) if values else 0.0
    left, right, top, bottom = 42, 770, 24, 250
    height = bottom - top
    points = []
    for i, item in enumerate(daily):
        x = left + (right - left) * i / 6
        y = bottom - ((float(item["value"]) / max_value) * height if max_value else 0)
        points.append({**item, "x": round(x, 2), "y": round(y, 2)})
    point_string = " ".join(f'{p["x"]},{p["y"]}' for p in points)
    area_points = f"{left},{bottom} {point_string} {right},{bottom}"

    return render(request, "admin/statistics_center.html", {
        "stats": {
            "orders": orders.count(),
            "products": products.count(),
            "customers": customers.count(),
            "sellers": SellerProfile.objects.count(),
            "revenue": total_revenue,
            "active_products": products.filter(is_active=True).count(),
            "active_sellers": SellerProfile.objects.filter(is_active=True).count(),
            "active_riders": DeliveryAgent.objects.filter(is_active=True).count(),
        },
        "recent_orders": orders.select_related("customer").order_by("-created_at")[:5],
        "points": points,
        "point_string": point_string,
        "area_points": area_points,
        "start": start,
        "today": today,
    })
