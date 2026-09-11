from decimal import Decimal, InvalidOperation
import uuid

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CustomerRegistrationForm
from .models import DeliveryAgent, DeliveryLocationPing, Order, OrderEvent, OrderItem, Product


def _customer_only(request):
    return not (request.user.is_staff or request.user.is_superuser)


def _record_order_event(order, event_type, note="", actor=None, delivery_agent=None):
    return OrderEvent.objects.create(
        order=order,
        event_type=event_type,
        note=note,
        actor=actor,
        delivery_agent=delivery_agent,
    )


def customer_register(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect("/admin/")
        return redirect("customer_dashboard")

    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
            except IntegrityError:
                form.add_error(
                    "username",
                    "Username exists. Please choose a different username.",
                )
            else:
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
                "Admin accounts can only be used in the Shopiva Admin Control Center.",
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
                    "This is an admin account. Please use the Shopiva Admin Control Center.",
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
    if not _customer_only(request):
        return redirect("/admin/")
    orders = Order.objects.filter(email__iexact=request.user.email).order_by("-created_at")
    return render(request, "accounts/dashboard.html", {"orders": orders[:5], "latest_order": orders.first()})


@login_required(login_url="customer_login")
def customer_orders(request):
    if not _customer_only(request):
        return redirect("/admin/")
    orders = Order.objects.filter(email__iexact=request.user.email).prefetch_related("events", "delivery_agent").order_by("-created_at")
    return render(request, "accounts/orders.html", {"orders": orders})


@login_required(login_url="customer_login")
def customer_delivery_location(request):
    """Return only the latest assigned delivery partner location for this customer."""
    if not _customer_only(request):
        return JsonResponse({"ok": False, "error": "Admin accounts use the admin delivery map."}, status=403)

    latest_order = (
        Order.objects.filter(email__iexact=request.user.email)
        .select_related("delivery_agent")
        .prefetch_related("events")
        .order_by("-created_at")
        .first()
    )

    if not latest_order or not latest_order.delivery_agent:
        return JsonResponse({"ok": True, "agent": None, "order": None})

    agent = latest_order.delivery_agent
    data = {
        "id": agent.id,
        "name": agent.display_name,
        "status": agent.get_status_display(),
        "latitude": float(agent.current_latitude) if agent.current_latitude is not None else None,
        "longitude": float(agent.current_longitude) if agent.current_longitude is not None else None,
        "updated": agent.last_location_at.isoformat() if agent.last_location_at else None,
        "live": agent.location_is_live,
        "accuracy": None,
    }

    latest_ping = agent.location_history.order_by("-recorded_at").first()
    if latest_ping and latest_ping.accuracy_meters is not None:
        data["accuracy"] = float(latest_ping.accuracy_meters)

    return JsonResponse(
        {
            "ok": True,
            "agent": data,
            "order": {
                "id": latest_order.id,
                "tracking_code": latest_order.tracking_code,
                "status": latest_order.get_status_display(),
            },
        }
    )


@login_required(login_url="customer_login")
def customer_profile(request):
    if not _customer_only(request):
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
    if not _customer_only(request):
        return redirect("/admin/")
    return render(request, "accounts/addresses.html")


@login_required(login_url="customer_login")
def customer_wishlist(request):
    if not _customer_only(request):
        return redirect("/admin/")
    return render(request, "accounts/wishlist.html")


@login_required(login_url="customer_login")
def delivery_portal(request):
    try:
        agent = request.user.delivery_agent_profile
    except DeliveryAgent.DoesNotExist:
        return redirect("/admin/")

    if not agent.is_active:
        return render(request, "delivery/not_authorized.html")

    assigned_orders = agent.orders.select_related("delivery_agent").prefetch_related("events").exclude(status="delivered").exclude(status="cancelled").order_by("-created_at")
    return render(
        request,
        "delivery/portal.html",
        {"agent": agent, "assigned_orders": assigned_orders},
    )


@login_required(login_url="customer_login")
def delivery_update_location(request):
    """Backward-compatible manual location update endpoint."""
    if request.method != "POST":
        return redirect("delivery_portal")

    try:
        agent = request.user.delivery_agent_profile
    except DeliveryAgent.DoesNotExist:
        return redirect("/admin/")

    if not agent.is_active:
        return redirect("/admin/")

    try:
        latitude = Decimal(request.POST.get("latitude", ""))
        longitude = Decimal(request.POST.get("longitude", ""))
    except (InvalidOperation, TypeError):
        return redirect("delivery_portal")

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return redirect("delivery_portal")

    now = timezone.now()
    agent.current_latitude = latitude.quantize(Decimal("0.000001"))
    agent.current_longitude = longitude.quantize(Decimal("0.000001"))
    agent.last_location_at = now
    agent.status = "on_delivery" if agent.orders.filter(status="out_for_delivery").exists() else "available"
    agent.save(update_fields=["current_latitude", "current_longitude", "last_location_at", "status"])
    DeliveryLocationPing.objects.create(
        agent=agent,
        latitude=agent.current_latitude,
        longitude=agent.current_longitude,
    )
    return redirect("delivery_portal")


@login_required(login_url="customer_login")
def delivery_ping_location(request):
    """Receive an automatic browser GPS ping from a delivery partner."""
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    try:
        agent = request.user.delivery_agent_profile
    except DeliveryAgent.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Delivery partner profile not found."}, status=403)

    if not agent.is_active:
        return JsonResponse({"ok": False, "error": "Delivery partner account is inactive."}, status=403)

    try:
        latitude = Decimal(str(request.POST.get("latitude", "")))
        longitude = Decimal(str(request.POST.get("longitude", "")))
    except (InvalidOperation, TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Invalid coordinates."}, status=400)

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return JsonResponse({"ok": False, "error": "Coordinates are out of range."}, status=400)

    def optional_decimal(field_name, minimum=None, maximum=None):
        raw = request.POST.get(field_name, "").strip()
        if not raw:
            return None
        try:
            value = Decimal(raw)
        except (InvalidOperation, TypeError, ValueError):
            return None
        if minimum is not None and value < minimum:
            return None
        if maximum is not None and value > maximum:
            return None
        return value

    accuracy = optional_decimal("accuracy", minimum=Decimal("0"), maximum=Decimal("100000"))
    speed = optional_decimal("speed", minimum=Decimal("0"), maximum=Decimal("100"))
    heading = optional_decimal("heading", minimum=Decimal("0"), maximum=Decimal("360"))

    now = timezone.now()
    latitude = latitude.quantize(Decimal("0.000001"))
    longitude = longitude.quantize(Decimal("0.000001"))

    agent.current_latitude = latitude
    agent.current_longitude = longitude
    agent.last_location_at = now
    agent.status = "on_delivery" if agent.orders.filter(status="out_for_delivery").exists() else "available"
    agent.save(update_fields=["current_latitude", "current_longitude", "last_location_at", "status"])

    DeliveryLocationPing.objects.create(
        agent=agent,
        latitude=latitude,
        longitude=longitude,
        accuracy_meters=accuracy.quantize(Decimal("0.01")) if accuracy is not None else None,
        speed_mps=speed.quantize(Decimal("0.01")) if speed is not None else None,
        heading_degrees=heading.quantize(Decimal("0.01")) if heading is not None else None,
    )

    return JsonResponse(
        {
            "ok": True,
            "updated_at": now.isoformat(),
            "latitude": float(latitude),
            "longitude": float(longitude),
            "status": agent.get_status_display(),
        }
    )


def home(request):
    products = Product.objects.filter(is_active=True).order_by("-id")
    discounted_products = products.filter(discount_percent__gt=0)

    # Build a rich hero rotation from featured items first, then live offers,
    # then the newest products so the homepage slideshow stays useful even
    # when an admin has not explicitly marked enough products as featured.
    featured_products = list(products.filter(is_featured=True)[:6])
    for product in discounted_products[:6]:
        if product not in featured_products and len(featured_products) < 6:
            featured_products.append(product)
    for product in products[:6]:
        if product not in featured_products and len(featured_products) < 6:
            featured_products.append(product)

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

    if request.method == "POST":
        action = request.POST.get("action", "")
        product_id = request.POST.get("product_id", "").strip()

        if product_id:
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except (Product.DoesNotExist, ValueError, TypeError):
                product = None

            if product is not None:
                if action == "remove":
                    cart_data.pop(str(product.id), None)
                elif action == "update":
                    try:
                        quantity = int(request.POST.get("quantity", "1"))
                    except (TypeError, ValueError):
                        quantity = 1

                    quantity = max(0, min(quantity, product.stock_quantity))
                    if quantity == 0:
                        cart_data.pop(str(product.id), None)
                    else:
                        cart_data[str(product.id)] = quantity

                request.session["cart"] = cart_data
                request.session.modified = True

        return redirect("cart")

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

            tracking_code = f"SPV-{uuid.uuid4().hex[:10].upper()}"
            order = Order.objects.create(
                customer_name=customer_name,
                email=email,
                phone=phone,
                address=address,
                total_amount=final_total,
                status="pending",
                payment_status="unpaid",
                tracking_code=tracking_code,
            )

            _record_order_event(
                order,
                "placed",
                note="Order placed through Shopiva checkout.",
                actor=request.user if request.user.is_authenticated else None,
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
