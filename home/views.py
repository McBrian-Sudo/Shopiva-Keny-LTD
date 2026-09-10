from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomerRegistrationForm
from .models import Order, OrderItem, Product


def customer_register(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect("/admin/")
        return redirect("customer_dashboard")

    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f"Welcome to Shopiva, {user.username}!")
            return redirect("customer_dashboard")
    else:
        form = CustomerRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def customer_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            messages.info(
                request,
                "Admin accounts can only be used in the Shopiva Admin Control Center."
            )
            return redirect("/admin/")
        return redirect("customer_dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user.is_staff or user.is_superuser:
                form.add_error(
                    None,
                    "This is an admin account. Please use the Shopiva Admin Control Center."
                )
            else:
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect("customer_dashboard")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def customer_logout(request):
    auth_logout(request)
    messages.success(request, "You have been signed out of Shopiva.")
    return redirect("customer_login")


@login_required(login_url="customer_login")
def customer_dashboard(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("/admin/")
    return render(request, "accounts/dashboard.html")


@login_required(login_url="customer_login")
def customer_orders(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("/admin/")

    orders = Order.objects.filter(email__iexact=request.user.email).order_by("-created_at")
    return render(request, "accounts/orders.html", {"orders": orders})


@login_required(login_url="customer_login")
def customer_profile(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("/admin/")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if email:
            request.user.email = email
            request.user.save(update_fields=["email"])
            messages.success(request, "Your profile has been updated.")
            return redirect("customer_profile")

    return render(request, "accounts/profile.html")


@login_required(login_url="customer_login")
def customer_addresses(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("/admin/")
    return render(request, "accounts/addresses.html")


@login_required(login_url="customer_login")
def customer_wishlist(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("/admin/")
    return render(request, "accounts/wishlist.html")


def home(request):
    products = Product.objects.filter(is_active=True).order_by("-id")
    featured_products = products.filter(is_featured=True)
    discounted_products = products.filter(discount_percent__gt=0)

    return render(
        request,
        "home.html",
        {
            "products": products,
            "featured_products": featured_products,
            "discounted_products": discounted_products,
        },
    )


def categories(request):
    categories = (
        Product.objects.filter(is_active=True)
        .exclude(category="")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    return render(request, "categories.html", {"categories": categories})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    return render(request, "product_detail.html", {"product": product})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    cart_data = request.session.get("cart", {})
    product_id_str = str(product.id)
    current_quantity = int(cart_data.get(product_id_str, 0))

    if product.stock_quantity > current_quantity:
        cart_data[product_id_str] = current_quantity + 1
        request.session["cart"] = cart_data
        request.session.modified = True

    return redirect("cart")


def _cart_items(cart_data):
    items = []
    total = Decimal("0.00")

    for product_id, raw_quantity in cart_data.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            quantity = max(0, int(raw_quantity))
        except (Product.DoesNotExist, TypeError, ValueError):
            continue

        if quantity <= 0 or product.stock_quantity <= 0:
            continue

        quantity = min(quantity, product.stock_quantity)
        unit_price = product.discounted_price
        subtotal = unit_price * quantity
        total += subtotal

        items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
                "unit_price": unit_price,
            }
        )

    return items, total


def cart(request):
    cart_data = request.session.get("cart", {})
    items, total = _cart_items(cart_data)

    request.session["cart"] = {
        str(item["product"].id): item["quantity"] for item in items
    }
    request.session.modified = True

    return render(request, "cart.html", {"items": items, "total": total})


def checkout(request):
    cart_data = request.session.get("cart", {})
    items, total = _cart_items(cart_data)

    if request.method == "POST":
        customer_name = request.POST.get("customer_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()

        if not all([customer_name, email, phone, address]) or not items:
            return render(
                request,
                "checkout.html",
                {
                    "items": items,
                    "total": total,
                    "error": "Please complete all customer details and make sure your cart is not empty.",
                },
            )

        with transaction.atomic():
            locked_items = []
            final_total = Decimal("0.00")

            for item in items:
                product = Product.objects.select_for_update().get(id=item["product"].id)
                quantity = item["quantity"]

                if not product.is_active or product.stock_quantity < quantity:
                    return render(
                        request,
                        "checkout.html",
                        {
                            "items": items,
                            "total": total,
                            "error": f"Sorry, {product.name} no longer has enough stock. Please review your cart.",
                        },
                    )

                unit_price = product.discounted_price
                subtotal = unit_price * quantity
                final_total += subtotal
                locked_items.append((product, quantity, unit_price))

            order = Order.objects.create(
                customer_name=customer_name,
                email=email,
                phone=phone,
                address=address,
                total_amount=final_total,
                status="pending",
            )

            for product, quantity, unit_price in locked_items:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=unit_price,
                )
                product.stock_quantity -= quantity
                product.save(update_fields=["stock_quantity"])

        request.session["cart"] = {}
        request.session.modified = True
        return redirect("order_success", order_id=order.id)

    return render(request, "checkout.html", {"items": items, "total": total})


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "order_success.html", {"order": order})


def products(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()

    product_list = Product.objects.filter(is_active=True).order_by("-id")

    if query:
        product_list = product_list.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__icontains=query)
        )

    if category:
        product_list = product_list.filter(category__iexact=category)

    categories_list = (
        Product.objects.filter(is_active=True)
        .exclude(category="")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    paginator = Paginator(product_list, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "products.html",
        {
            "products": page_obj,
            "page_obj": page_obj,
            "categories": categories_list,
            "query": query,
            "selected_category": category,
        },
    )
