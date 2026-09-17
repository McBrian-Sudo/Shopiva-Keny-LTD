from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .models import Notification


def _role_for(user):
    if user.is_staff or user.is_superuser:
        return "admin"
    try:
        user.seller_profile
        return "seller"
    except Exception:
        return "customer"


@login_required

def notification_center(request):
    role = _role_for(request.user)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "read_all":
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        elif action == "read" and request.POST.get("notification_id"):
            Notification.objects.filter(id=request.POST["notification_id"], user=request.user).update(is_read=True)
        return redirect(request.path)

    notifications = list(Notification.objects.filter(user=request.user).order_by("-created_at")[:100])
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return render(request, "accounts/notifications.html", {
        "notifications": notifications,
        "unread_count": unread_count,
        "role": role,
    })
