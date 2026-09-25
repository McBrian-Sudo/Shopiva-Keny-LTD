import json
import re

from django.db.models import Q
from django.http import JsonResponse

from .models import Order, Product, WishlistItem
from .nia_core import call_nia


def _catalog(limit=80):
    return list(
        Product.objects.filter(is_active=True)
        .order_by("-is_featured", "-discount_percent", "-id")[:limit]
    )


def _fallback(question, products):
    words = {w.lower() for w in re.findall(r"[a-zA-Z0-9]+", question) if len(w) > 2}
    ranked = []
    for product in products:
        text = f"{product.name} {product.description} {product.category} {product.promo_text}".lower()
        score = sum(1 for word in words if word in text)
        if score:
            ranked.append((score, product))
    ranked.sort(key=lambda x: (-x[0], -x[1].discount_percent, x[1].price))
    picks = [p for _, p in ranked[:5]]
    if not picks:
        picks = sorted(products, key=lambda p: (-p.discount_percent, p.price))[:5]
    if not picks:
        return {"answer": "I don't have products to recommend yet. Add products in the Shopiva Control Center.", "products": []}
    answer = "Here are the Shopiva products that best match your request:"
    return {
        "answer": answer,
        "products": [
            {"id": p.id, "name": p.name, "price": float(p.discounted_price), "discount": p.discount_percent}
            for p in picks
        ],
    }


def shop_assistant(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    question = request.POST.get("question", "").strip()
    if not question:
        return JsonResponse({"ok": False, "error": "Please ask a shopping question."}, status=400)

    if request.user.is_authenticated and (
        request.user.is_staff
        or getattr(request.user, "seller_profile", None) is not None
        or getattr(request.user, "delivery_agent_profile", None) is not None
    ):
        return JsonResponse({"ok": False, "error": "Customer Nia is only available to customer accounts."}, status=403)

    products = _catalog()
    fallback = _fallback(question, products)

    customer_orders = []
    cart_items = []
    if request.user.is_authenticated and not request.user.is_staff:
        customer_orders = list(
            Order.objects.filter(email__iexact=request.user.email)
            .order_by("-created_at")
            .values("id", "tracking_code", "status", "payment_status", "total_amount")[:8]
        )
        cart = request.session.get("cart", {})
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=int(product_id), is_active=True)
                qty = max(1, int(quantity))
            except (Product.DoesNotExist, TypeError, ValueError):
                continue
            cart_items.append({
                "id": product.id,
                "name": product.name,
                "quantity": qty,
                "unit_price": str(product.discounted_price),
                "line_total": str(product.discounted_price * qty),
            })

        q_lower = question.lower()
        if "cart" in q_lower or "basket" in q_lower:
            fallback["answer"] = (
                "Your current cart is: " + "; ".join(
                    f"{item['name']} × {item['quantity']}" for item in cart_items
                )
                if cart_items else "Your cart is currently empty."
            )
        elif "order" in q_lower and any(
            word in q_lower for word in ("status", "track", "where", "latest", "recent")
        ):
            if customer_orders:
                latest = customer_orders[0]
                fallback["answer"] = (
                    f"Your latest order is #{latest['id']} ({latest['tracking_code']}). "
                    f"Status: {latest['status']}. Payment: {latest['payment_status']}."
                )
            else:
                fallback["answer"] = "I don't see any orders in your customer account yet."

    catalog = [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "description": p.description[:400],
            "price": str(p.discounted_price),
            "original_price": str(p.price),
            "discount_percent": p.discount_percent,
            "stock": p.stock_quantity,
        }
        for p in products
    ]

    profile = "Guest shopper."
    if request.user.is_authenticated:
        wishlist_ids = list(
            WishlistItem.objects.filter(user=request.user)
            .values_list("product_id", flat=True)[:20]
        )
        recent_orders = list(
            Order.objects.filter(email__iexact=request.user.email)
            .order_by("-created_at")
            .values_list("id", "status")[:5]
        )
        profile = {
            "wishlist_product_ids": wishlist_ids,
            "recent_orders": recent_orders,
            "current_cart": request.session.get("cart", {}),
        }

    result = call_nia(
        "Shopping Copilot",
        {"customer": profile, "catalog": catalog},
        question,
        '{"answer": "string", "product_ids": [integer]}',
    )
    if result.get("ai"):
        data = result.get("data") or {}
        try:
            ids = []
            for value in data.get("product_ids", []):
                try:
                    value = int(value)
                except (TypeError, ValueError):
                    continue
                if value in {p.id for p in products} and value not in ids:
                    ids.append(value)
                if len(ids) >= 5:
                    break
        except (TypeError, ValueError):
            ids = []
        selected = {p.id: p for p in products}
        return JsonResponse(
            {
                "ok": True,
                "ai": True,
                "answer": str(data.get("answer") or fallback["answer"]),
                "products": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "price": float(p.discounted_price),
                        "discount": p.discount_percent,
                    }
                    for p in [selected[i] for i in ids]
                ],
            }
        )

    return JsonResponse({"ok": True, "ai": False, **fallback})
