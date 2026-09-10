from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from .models import Order, OrderItem, Product


@staff_member_required(login_url="/admin/login/")
def business_intelligence(request):
    today = timezone.localdate()
    orders = Order.objects.exclude(status="cancelled")
    paid_orders = orders.filter(payment_status="paid")

    revenue = orders.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")
    paid_revenue = paid_orders.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")
    order_count = orders.count()
    average_order_value = revenue / order_count if order_count else Decimal("0.00")

    customer_values = orders.values("email").annotate(order_count=Count("id"))
    repeat_customers = customer_values.filter(order_count__gt=1).count()

    quantity_value = ExpressionWrapper(
        F("quantity") * F("price"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    top_products = (
        OrderItem.objects.filter(order__in=orders)
        .values("product__name")
        .annotate(units=Sum("quantity"), sales=Sum(quantity_value))
        .order_by("-sales")[:10]
    )

    top_categories = (
        OrderItem.objects.filter(order__in=orders)
        .values("product__category")
        .annotate(units=Sum("quantity"), sales=Sum(quantity_value))
        .order_by("-sales")[:10]
    )

    daily_sales = (
        orders.filter(created_at__gte=timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time())))
        .values("created_at__date")
        .annotate(orders=Count("id"), revenue=Sum("total_amount"))
        .order_by("created_at__date")
    )

    stock_value = sum(
        (product.price or Decimal("0.00")) * product.stock_quantity
        for product in Product.objects.filter(is_active=True)
    )

    context = {
        "stats": {
            "orders": order_count,
            "revenue": revenue,
            "paid_revenue": paid_revenue,
            "average_order_value": average_order_value,
            "repeat_customers": repeat_customers,
            "active_products": Product.objects.filter(is_active=True).count(),
            "stock_value": stock_value,
        },
        "top_products": top_products,
        "top_categories": top_categories,
        "daily_sales": daily_sales,
    }
    return render(request, "admin/business_intelligence.html", context)
