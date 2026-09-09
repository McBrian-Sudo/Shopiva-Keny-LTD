from decimal import Decimal

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Order, OrderItem, Product


def home(request):
    products = Product.objects.all().order_by("-id")
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
        Product.objects
        .filter(is_active=True)
        .exclude(category="")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    return render(
        request,
        "categories.html",
        {
            "categories": categories,
        },
    )


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
        },
    )


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get("cart", {})
    product_id_str = str(product.id)

    cart[product_id_str] = cart.get(product_id_str, 0) + 1

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


def cart(request):
    cart_data = request.session.get("cart", {})

    items = []
    total = Decimal("0.00")

    for product_id, quantity in cart_data.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        quantity = int(quantity)
        subtotal = product.price * quantity
        total += subtotal

        items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    return render(
        request,
        "cart.html",
        {
            "items": items,
            "total": total,
        },
    )


def checkout(request):
    cart_data = request.session.get("cart", {})

    items = []
    total = Decimal("0.00")

    for product_id, quantity in cart_data.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        quantity = int(quantity)
        subtotal = product.price * quantity
        total += subtotal

        items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

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
                    "error": (
                        "Please complete all customer details "
                        "and make sure your cart is not empty."
                    ),
                },
            )

        with transaction.atomic():
            order = Order.objects.create(
                customer_name=customer_name,
                email=email,
                phone=phone,
                address=address,
                total_amount=total,
                status="pending",
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    quantity=item["quantity"],
                    price=item["product"].price,
                )

        request.session["cart"] = {}
        request.session.modified = True

        return redirect("order_success", order_id=order.id)

    return render(
        request,
        "checkout.html",
        {
            "items": items,
            "total": total,
        },
    )


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return render(
        request,
        "order_success.html",
        {
            "order": order,
        },
    )


def products(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()

    product_list = Product.objects.filter(
        is_active=True
    ).order_by("-id")

    if query:
        product_list = product_list.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__icontains=query)
        )

    if category:
        product_list = product_list.filter(
            category__iexact=category
        )

    categories_list = (
        Product.objects
        .filter(is_active=True)
        .exclude(category="")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    paginator = Paginator(product_list, 12)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

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
