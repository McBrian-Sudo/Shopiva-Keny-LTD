import json
import os
import re

from django.db.models import Q
from django.http import JsonResponse

from .models import Order, Product, WishlistItem


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

    products = _catalog()
    fallback = _fallback(question, products)

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return JsonResponse({"ok": True, "ai": False, **fallback})

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
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
        if request.user.is_authenticated and not request.user.is_staff:
            wishlist_ids = list(
                WishlistItem.objects.filter(user=request.user)
                .values_list("product_id", flat=True)[:20]
            )
            recent_orders = list(
                Order.objects.filter(email__iexact=request.user.email)
                .order_by("-created_at")
                .values_list("id", "status")[:5]
            )
            profile = f"Customer wishlist product IDs: {wishlist_ids}; recent orders: {recent_orders}."

        prompt = f"""
You are Shopiva Kenya's shopping AI. Help the customer find products in the supplied catalog.
Never invent a product, price, stock level, discount, delivery promise, or payment result.
Use Kenya-friendly language and KSh pricing.
If the request is vague, ask one useful follow-up question.
Recommend up to 5 catalog products.
Return ONLY valid JSON with keys: answer (string), product_ids (array of integers).
Customer context: {profile}
Customer request: {question}
Catalog: {json.dumps(catalog, ensure_ascii=False)}
"""
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
            input=prompt,
        )
        raw = response.output_text.strip()
        data = json.loads(raw)
        valid_ids = {p.id for p in products}
        ids = [int(x) for x in data.get("product_ids", []) if int(x) in valid_ids][:5]
        selected = {p.id: p for p in products}
        return JsonResponse(
            {
                "ok": True,
                "ai": True,
                "answer": str(data.get("answer", fallback["answer"])),
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
    except Exception:
        # AI is an enhancement; shopping must remain usable if the provider is
        # unavailable, misconfigured, or temporarily rate-limited.
        return JsonResponse({"ok": True, "ai": False, **fallback})
