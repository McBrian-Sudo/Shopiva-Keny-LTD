from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import Order


@login_required(login_url="customer_login")
def customer_order_tracking(request, order_id):
    if request.user.is_staff or request.user.is_superuser:
        raise Http404

    order = get_object_or_404(
        Order.objects.select_related("delivery_agent").prefetch_related("items__product", "events"),
        id=order_id,
        email__iexact=request.user.email,
    )

    return render(
        request,
        "accounts/order_tracking.html",
        {
            "order": order,
            "events": order.events.all(),
        },
    )
