from decimal import Decimal
import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, F, Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET

from .models import DeliveryAgent, NiaAuditLog, Order, OrderItem, PaymentTransaction, Product, SellerPayoutRequest, SellerProfile


def _money(value):
    return str(value or Decimal("0.00"))


def seller_performance(limit=10):
    rows=[]
    for seller in SellerProfile.objects.filter(is_active=True).select_related("user"):
        sales=OrderItem.objects.filter(seller=seller).aggregate(v=Sum(F("price")*F("quantity")))["v"] or Decimal("0.00")
        orders=Order.objects.filter(items__seller=seller).distinct()
        rows.append({"seller":seller.business_name or seller.user.username,"orders":orders.count(),"delivered":orders.filter(status="delivered").count(),"sales":_money(sales),"available_balance":_money(seller.wallet.available_balance if hasattr(seller,"wallet") else 0)})
    return sorted(rows,key=lambda x:Decimal(x["sales"]),reverse=True)[:limit]


def build_admin_context():
    now=timezone.now(); today=timezone.localdate(); week=now-timedelta(days=7); month=now-timedelta(days=30)
    products=Product.objects.all(); orders=Order.objects.all(); payments=PaymentTransaction.objects.all(); riders=DeliveryAgent.objects.all()
    rev=lambda qs: _money(qs.exclude(status="cancelled").aggregate(v=Sum("total_amount"))["v"])
    mpesa=payments.filter(method="mpesa"); mw=mpesa.filter(created_at__gte=week); attempts=mw.count(); success=mw.filter(status="paid").count()
    User=get_user_model()
    try:
        from support.models import SupportTicket
        support={"open":SupportTicket.objects.filter(status__in=("open","in_progress","waiting_for_customer")).count(),"urgent":SupportTicket.objects.filter(status="open",priority="urgent").count()}
    except Exception:
        support={"open":0,"urgent":0}
    return {
        "products":{"total":products.count(),"active":products.filter(is_active=True).count(),"low_stock":products.filter(is_active=True,stock_quantity__lte=5,stock_quantity__gt=0).count(),"out_of_stock":products.filter(is_active=True,stock_quantity=0).count()},
        "orders":{"total":orders.count(),"pending":orders.filter(status="pending").count(),"paid":orders.filter(payment_status="paid").count(),"failed_payment":orders.filter(payment_status="failed").count(),"delivered":orders.filter(status="delivered").count(),"delayed":orders.filter(status__in=("processing","shipped","out_for_delivery")).count(),"today":orders.filter(created_at__date=today).count()},
        "payments":{"mpesa_success_week":success,"mpesa_attempts_week":attempts,"mpesa_pending":mpesa.filter(status="pending").count(),"mpesa_failed":mpesa.filter(status="failed").count(),"success_rate_week":round(success*100/attempts,2) if attempts else 0},
        "sellers":{"total":SellerProfile.objects.count(),"active":SellerProfile.objects.filter(is_active=True).count(),"performance":seller_performance()},
        "customers":{"total":User.objects.filter(is_staff=False).count(),"recent_signups":User.objects.filter(is_staff=False,date_joined__gte=week).count()},
        "delivery":{"active":riders.filter(is_active=True).count(),"available":riders.filter(is_active=True,status="available").count(),"on_delivery":riders.filter(is_active=True,status="on_delivery").count(),"unassigned_orders":orders.filter(delivery_agent__isnull=True,status__in=("confirmed","paid","packed","processing","shipped","out_for_delivery")).count()},
        "approvals":{"pending_staff":riders.filter(is_active=False).count()},
        "revenue":{"today":rev(orders.filter(created_at__date=today)),"week":rev(orders.filter(created_at__gte=week)),"month":rev(orders.filter(created_at__gte=month)),"pending_payouts":_money(SellerPayoutRequest.objects.filter(status__in=("requested","processing")).aggregate(v=Sum("amount"))["v"])},
        "support":support,
        "health":{"nia_failed_audit_events_week":NiaAuditLog.objects.filter(action__icontains="failed",created_at__gte=week).count()},
        "categories":list(products.values("category").annotate(count=Count("id")).order_by("-count")[:12]),
    }


def daily_digest():
    c=build_admin_context()
    return f"Today: {c['orders']['today']} orders, KSh {c['revenue']['today']} recorded revenue, {c['payments']['mpesa_failed']} failed M-PESA transactions, {c['payments']['mpesa_pending']} pending M-PESA transactions, {c['products']['low_stock']} low-stock products, and {c['approvals']['pending_staff']} staff approvals waiting."


def allowed_order_search(question):
    q=question.lower(); qs=Order.objects.all(); filters=[]
    m=re.search(r"(?:over|above|greater than|more than)\s*k?sh?\s*([\d,]+)",q)
    if m:
        amount=Decimal(m.group(1).replace(",","")); qs=qs.filter(total_amount__gt=amount); filters.append(f"total > KSh {amount:,.2f}")
    m=re.search(r"(?:under|below|less than)\s*k?sh?\s*([\d,]+)",q)
    if m:
        amount=Decimal(m.group(1).replace(",","")); qs=qs.filter(total_amount__lt=amount); filters.append(f"total < KSh {amount:,.2f}")
    for town in ("nairobi","eldoret","mombasa","kisumu","nakuru","kitale","thika","meru","kakamega"):
        if town in q:
            qs=qs.filter(Q(delivery_town__icontains=town)|Q(address__icontains=town)); filters.append(f"destination contains {town.title()}"); break
    if "today" in q: qs=qs.filter(created_at__date=timezone.localdate()); filters.append("today")
    if "failed payment" in q or "failed payments" in q: qs=qs.filter(payment_status="failed"); filters.append("payment failed")
    if not filters:return None
    return filters,list(qs.order_by("-created_at").values("id","tracking_code","status","payment_status","total_amount","delivery_town","delivery_county")[:20])


def answer_admin_question(question):
    c=build_admin_context(); q=question.lower(); found=allowed_order_search(question)
    if found:
        filters,rows=found
        return {"answer":f"I found {len(rows)} matching order(s) using: {', '.join(filters)}.","orders":rows,"context":c}
    if "digest" in q or ("today" in q and ("summary" in q or "activity" in q)): return {"answer":daily_digest(),"context":c}
    if "success rate" in q and "mpesa" in q:return {"answer":f"This week's M-PESA success rate is {c['payments']['success_rate_week']}% based on {c['payments']['mpesa_attempts_week']} recorded attempts.","context":c}
    if "failed" in q and ("payment" in q or "mpesa" in q):return {"answer":f"There are {c['orders']['failed_payment']} orders with failed payment status and {c['payments']['mpesa_failed']} failed M-PESA transactions.","context":c}
    if "low stock" in q:return {"answer":f"There are {c['products']['low_stock']} active low-stock products and {c['products']['out_of_stock']} active out-of-stock products.","context":c}
    if "seller" in q and any(x in q for x in ("top","bottom","performance","sales")):return {"answer":"Here is current seller performance data, ordered by recorded sales.","sellers":c["sellers"]["performance"],"context":c}
    return {"answer":"Nia can report products, orders, M-PESA, sellers, customers, delivery, approvals, revenue, support and category data.","context":c}


@require_GET
def nia_dashboard_context(request):
    if not request.user.is_authenticated:return JsonResponse({"ok":False,"error":"Authentication required."},status=401)
    user=request.user
    if user.is_staff:
        c=build_admin_context()
        stats={"primary_value":c["orders"]["pending"],"primary_label":"Pending orders","secondary_value":c["payments"]["mpesa_failed"],"secondary_label":"Failed M-PESA","tertiary_value":c["products"]["low_stock"],"tertiary_label":"Low-stock products"}
    else:
        seller=getattr(user,"seller_profile",None)
        if seller and seller.is_active:
            products=Product.objects.filter(seller=seller,is_active=True); orders=Order.objects.filter(items__seller=seller).distinct(); today=timezone.localdate()
            sales=OrderItem.objects.filter(seller=seller,order__created_at__date=today).aggregate(v=Sum(F("price")*F("quantity")))["v"] or Decimal("0.00")
            stats={"primary_value":orders.filter(status="pending").count(),"primary_label":"Pending orders","secondary_value":products.filter(stock_quantity__lte=5).count(),"secondary_label":"Low-stock products","tertiary_value":f"KSh {sales:,.0f}","tertiary_label":"Today's sales"}
        else:
            orders=Order.objects.filter(email__iexact=user.email)
            stats={"primary_value":orders.count(),"primary_label":"My orders","secondary_value":orders.filter(status__in=("pending","processing","shipped","out_for_delivery")).count(),"secondary_label":"Active orders","tertiary_value":user.shopiva_wishlist.count(),"tertiary_label":"Wishlist items"}
    return JsonResponse({"ok":True,"role":"admin" if user.is_staff else ("seller" if getattr(user,"seller_profile",None) and user.seller_profile.is_active else "customer"),"stats":stats})
