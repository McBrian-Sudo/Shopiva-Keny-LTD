from functools import wraps

from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render


def seller_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect("/admin/")
        if hasattr(request.user, "seller_profile"):
            return redirect("seller_dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            seller = getattr(user, "seller_profile", None)
            if not seller or not seller.is_active:
                form.add_error(None, "This account is not an active Shopiva seller account.")
            else:
                auth_login(request, user)
                messages.success(request, f"Welcome back, {seller.business_name or user.username}!")
                return redirect("seller_dashboard")
    else:
        form = AuthenticationForm(request)

    return render(request, "seller/login.html", {"form": form})


def seller_logout(request):
    auth_logout(request)
    messages.success(request, "You have been signed out of the seller portal.")
    return redirect("seller_login")


def seller_login_required(view_func):
    """Require an authenticated, active Shopiva seller for seller-only pages."""
    @wraps(view_func)
    @login_required(login_url="seller_login")
    def wrapped(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return redirect("/admin/")
        seller = getattr(request.user, "seller_profile", None)
        if not seller or not seller.is_active:
            messages.error(request, "Please sign in with an active Shopiva seller account.")
            return redirect("seller_login")
        return view_func(request, *args, **kwargs)

    return wrapped
