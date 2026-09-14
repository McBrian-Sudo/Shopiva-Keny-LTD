from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.contrib.auth import logout


def privacy_policy(request):
    return render(request, "legal/privacy.html")


def terms_of_service(request):
    return render(request, "legal/terms.html")


def account_deletion(request):
    if not request.user.is_authenticated:
        return redirect("customer_login")
    if request.user.is_staff or request.user.is_superuser:
        return render(request, "legal/account_deletion.html", {"blocked": True})

    if request.method == "POST":
        user = request.user
        confirm = request.POST.get("confirm", "").strip().upper()
        if confirm != "DELETE":
            return render(request, "legal/account_deletion.html", {"error": "Type DELETE to confirm permanent account deletion."})

        with transaction.atomic():
            # Remove app-account data that is not needed for legally required transaction records.
            user.shopiva_addresses.all().delete()
            user.shopiva_wishlist.all().delete()
            user.shopiva_notifications.all().delete()
            user.shopiva_reviews.all().delete()

            # Preserve legally/audit-relevant order and payment records, but remove direct customer identifiers.
            for order in user_order_qs(user).select_for_update():
                order.customer_name = "Deleted Shopiva Customer"
                order.email = f"deleted-order-{order.id}@shopiva.invalid"
                order.phone = ""
                order.address = "Deleted customer address"
                order.delivery_latitude = None
                order.delivery_longitude = None
                order.save(update_fields=[
                    "customer_name", "email", "phone", "address",
                    "delivery_latitude", "delivery_longitude"
                ])
                order.payments.update(phone="", raw_response={})

            username = user.username
            user.delete()

        logout(request)
        return render(request, "legal/account_deleted.html", {"username": username, "deleted_at": timezone.now()})

    return render(request, "legal/account_deletion.html", {"blocked": False})


def user_order_qs(user):
    from .models import Order
    return Order.objects.filter(email__iexact=user.email)
