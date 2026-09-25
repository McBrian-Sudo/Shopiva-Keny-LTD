import json
import os
from decimal import Decimal

from django.db.models import Count, Sum
from django.http import JsonResponse

from .models import Order, OrderItem, Product, SellerProfile, SellerWallet


def seller_profile_for(request):
    if not request.user.is_authenticated:
        return None
    seller = getattr(request.user, "seller_profile", None)
    if seller and seller.is_active:
        return seller
    return None


def _seller_snapshot(seller):
    products = Product.objects.filter(seller=seller)
    items = OrderItem.objects.filter(seller=seller)
    orders = Order.objects.filter(items__seller=seller).distinct()
    wallet, _ = SellerWallet.objects.get_or_create(seller=seller)

    return {
        "seller": seller.business_name or seller.user.username,
        "products": {
            "total": products.count(),
            "live": products.filter(is_active=True).count(),
            "low_stock": products.filter(is_active=True, stock_quantity__lte=5, stock_quantity__gt=0).count(),
            "out_of_stock": products.filter(is_active=True, stock_quantity=0).count(),
            "units": products.aggregate(total=Sum("stock_quantity"))["total"] or 0,
        },
        "orders": {
            "total": orders.count(),
            "pending": orders.filter(status="pending").count(),
            "paid": orders.filter(payment_status="paid").count(),
            "delivered": orders.filter(status="delivered").count(),
        },
        "wallet": {
            "pending_balance": str(wallet.pending_balance),
            "available_balance": str(wallet.available_balance),
            "total_sales": str(wallet.total_sales),
            "total_commission": str(wallet.total_commission),
        },
    }


def _seller_fallback(question, seller):
    q = question.lower()
    products = Product.objects.filter(seller=seller, is_active=True)
    orders = Order.objects.filter(items__seller=seller).distinct()
    wallet, _ = SellerWallet.objects.get_or_create(seller=seller)

    if "low stock" in q or "low-stock" in q:
        rows = products.filter(stock_quantity__lte=5).order_by("stock_quantity", "name")[:10]
        if not rows:
            return "You currently have no live products at or below 5 units of stock."
        return "Your low-stock products:\n" + "\n".join(
            f"• {p.name}: {p.stock_quantity} unit(s)" for p in rows
        )

    if any(word in q for word in ("out of stock", "out-of-stock", "sold out")):
        rows = products.filter(stock_quantity=0).order_by("name")[:10]
        if not rows:
            return "You currently have no live products that are out of stock."
        return "Your out-of-stock products:\n" + "\n".join(f"• {p.name}" for p in rows)

    if "pending order" in q or ("pending" in q and "order" in q):
        return f"You have {orders.filter(status='pending').count()} pending order(s)."

    if "paid order" in q or ("paid" in q and "order" in q):
        return f"You have {orders.filter(payment_status='paid').count()} paid order(s) in your seller order queue."

    if any(word in q for word in ("sales", "revenue", "earnings", "earned")):
        return (
            f"Your recorded sales are KSh {wallet.total_sales:,.2f}. "
            f"Your pending seller balance is KSh {wallet.pending_balance:,.2f}, "
            f"and your available payout balance is KSh {wallet.available_balance:,.2f}."
        )

    if any(word in q for word in ("commission", "fee", "shopiva fee")):
        return f"Shopiva has recorded KSh {wallet.total_commission:,.2f} in platform commission against your sales."

    if any(word in q for word in ("product", "listing", "catalog")) and any(
        word in q for word in ("how many", "count", "total", "number")
    ):
        return (
            f"You have {products.count()} active product(s) in your seller catalogue, "
            f"with {products.filter(stock_quantity__lte=5).count()} at or below 5 units."
        )

    if "help" in q or "what can" in q:
        return (
            "I can help with your products, stock, orders, sales, commissions and payout balances. "
            "Examples: “Which products are low stock?” or “How much is available for payout?”"
        )

    return (
        "I can help with your Shopiva seller operations. Try asking about low stock, "
        "pending orders, paid orders, sales, commissions or payout balance."
    )


def seller_assistant(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)
    seller = seller_profile_for(request)
    if not seller:
        return JsonResponse({"ok": False, "error": "Active seller access is required."}, status=403)

    question = request.POST.get("question", "").strip()
    if not question:
        return JsonResponse({"ok": False, "error": "Please ask a seller question."}, status=400)

    fallback = _seller_fallback(question, seller)
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return JsonResponse({"ok": True, "ai": False, "answer": fallback})

    snapshot = _seller_snapshot(seller)
    prompt = f"""
You are Shopiva Seller Copilot for one authenticated seller.
Use only the seller's supplied Shopiva data. Never reveal another seller's data.
Never invent stock, orders, money, commissions, payout availability, product details, or payment results.
Do not change records or claim to have changed anything.
Answer briefly in clear Kenyan business language and use KSh.
Seller snapshot:
{json.dumps(snapshot, ensure_ascii=False, default=str)}
Seller question:
{question}
"""
    try:
        from openai import OpenAI

        response = OpenAI(api_key=api_key).responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
            input=prompt,
        )
        answer = response.output_text.strip()
        return JsonResponse({"ok": True, "ai": True, "answer": answer or fallback})
    except Exception:
        return JsonResponse({"ok": True, "ai": False, "answer": fallback})
