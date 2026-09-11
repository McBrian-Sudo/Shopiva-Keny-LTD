from decimal import Decimal
import json
import os
import uuid

from django import forms
from django.contrib import admin
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User
from django.db.models import ProtectedError, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone

from .voice_ai import speak_text, transcribe_voice
from .models import CustomerAddress, DeliveryAgent, Order, OrderEvent, OrderItem, PaymentTransaction, Product, SellerProfile, SellerSettlement, SellerWallet, WishlistItem


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            "name",
            "sku",
            "description",
            "category",
            "price",
            "discount_percent",
            "stock_quantity",
            "promo_text",
            "image",
            "is_featured",
            "is_active",
            "seller",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "promo_text": forms.TextInput(attrs={"placeholder": "Optional promotion text"}),
        }


class ShopivaAdminSite(admin.AdminSite):
    site_header = "Shopiva Control Center"
    site_title = "Shopiva Admin"
    index_title = "Store Operations"
    index_template = "admin/index.html"

    def _stats(self):
        today = timezone.localdate()
        orders = Order.objects.all()
        products = Product.objects.all()
        return {
            "products": products.count(),
            "active_products": products.filter(is_active=True).count(),
            "low_stock": products.filter(stock_quantity__lte=5, is_active=True).count(),
            "orders": orders.count(),
            "pending_orders": orders.filter(status="pending").count(),
            "processing_orders": orders.filter(status__in=["confirmed", "paid", "packed", "processing", "shipped"]).count(),
            "delivered_orders": orders.filter(status="delivered").count(),
            "assigned_orders": orders.exclude(delivery_agent__isnull=True).exclude(status__in=["delivered", "cancelled"]).count(),
            "today_orders": orders.filter(created_at__date=today).count(),
            "revenue": orders.exclude(status="cancelled").aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00"),
        }

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        orders = Order.objects.select_related("delivery_agent").all()
        products = Product.objects.all()
        extra_context.update(
            {
                "shopiva_stats": self._stats(),
                "recent_orders": orders.order_by("-created_at")[:8],
                "low_stock_products": products.filter(stock_quantity__lte=5, is_active=True).order_by("stock_quantity", "name")[:8],
                "recent_products": products.order_by("-id")[:6],
                "active_delivery_agents": DeliveryAgent.objects.filter(is_active=True).select_related("user").order_by("user__username"),
            }
        )
        return super().index(request, extra_context=extra_context)

    def logout(self, request, extra_context=None):
        auth_logout(request)
        return redirect("shopiva_admin:login")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("products/", self.admin_view(self.product_manager), name="product_manager"),
            path("products/add/", self.admin_view(self.product_add), name="product_add"),
            path("products/<int:product_id>/edit/", self.admin_view(self.product_edit), name="product_edit"),
            path("products/<int:product_id>/delete/", self.admin_view(self.product_delete), name="product_delete"),
            path("ai-assistant/", self.admin_view(self.ai_assistant), name="ai_assistant"),
            path("ai-voice/transcribe/", self.admin_view(transcribe_voice), name="ai_voice_transcribe"),
            path("delivery-map/", self.admin_view(self.delivery_map), name="delivery_map"),
            path("delivery-locations/", self.admin_view(self.delivery_locations), name="delivery_locations"),
        ]
        return custom_urls + urls

    def delivery_map(self, request):
        context = {
            **self.each_context(request),
            "shopiva_stats": self._stats(),
            "delivery_agents": DeliveryAgent.objects.filter(is_active=True).select_related("user").order_by("user__username"),
            "recent_orders": Order.objects.select_related("delivery_agent").order_by("-created_at")[:15],
        }
        return TemplateResponse(request, "admin/delivery_map.html", context)

    def delivery_locations(self, request):
        agents = DeliveryAgent.objects.filter(is_active=True).select_related("user")
        data = []
        for agent in agents:
            if agent.current_latitude is None or agent.current_longitude is None:
                continue
            data.append(
                {
                    "name": agent.display_name,
                    "status": agent.get_status_display(),
                    "latitude": float(agent.current_latitude),
                    "longitude": float(agent.current_longitude),
                    "updated": agent.last_location_at.isoformat() if agent.last_location_at else None,
                }
            )
        return JsonResponse({"agents": data, "updated_at": timezone.now().isoformat()})

    def product_manager(self, request):
        query = request.GET.get("q", "").strip()
        category = request.GET.get("category", "").strip()
        status = request.GET.get("status", "").strip()

        product_list = Product.objects.all().order_by("-id")
        if query:
            product_list = product_list.filter(name__icontains=query)
        if category:
            product_list = product_list.filter(category__iexact=category)
        if status == "active":
            product_list = product_list.filter(is_active=True)
        elif status == "inactive":
            product_list = product_list.filter(is_active=False)
        elif status == "low":
            product_list = product_list.filter(is_active=True, stock_quantity__lte=5)

        categories = (
            Product.objects.exclude(category="")
            .values_list("category", flat=True)
            .distinct()
            .order_by("category")
        )

        context = {
            **self.each_context(request),
            "products": product_list,
            "categories": categories,
            "query": query,
            "selected_category": category,
            "selected_status": status,
            "product_count": product_list.count(),
        }
        return TemplateResponse(request, "admin/products/manager.html", context)

    def product_add(self, request):
        if request.method == "POST":
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect("shopiva_admin:product_manager")
        else:
            form = ProductForm()

        context = {**self.each_context(request), "form": form, "page_title": "Add Product", "mode": "add"}
        return TemplateResponse(request, "admin/products/form.html", context)

    def product_edit(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        if request.method == "POST":
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                return redirect("shopiva_admin:product_manager")
        else:
            form = ProductForm(instance=product)

        context = {
            **self.each_context(request),
            "form": form,
            "product": product,
            "page_title": "Edit Product",
            "mode": "edit",
        }
        return TemplateResponse(request, "admin/products/form.html", context)

    def product_delete(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        if request.method == "POST":
            try:
                product.delete()
            except ProtectedError:
                product.is_active = False
                product.save(update_fields=["is_active"])
            return redirect("shopiva_admin:product_manager")

        context = {**self.each_context(request), "product": product}
        return TemplateResponse(request, "admin/products/delete.html", context)

    def ai_assistant(self, request):
        if request.method != "POST":
            return JsonResponse({"answer": "Ask me about products, orders, stock, revenue, deliveries, or Shopiva operations."})

        question = request.POST.get("question", "").strip()
        products = Product.objects.all()
        orders = Order.objects.all()
        agents = DeliveryAgent.objects.filter(is_active=True)
        payments = PaymentTransaction.objects.select_related("order")

        # When configured, use a real generative model for richer operational
        # answers. The deterministic rules below remain as a safe fallback.
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if api_key and question:
            try:
                from openai import OpenAI

                snapshot = {
                    "products": products.count(),
                    "active_products": products.filter(is_active=True).count(),
                    "low_stock": list(products.filter(is_active=True, stock_quantity__lte=5).values("id", "name", "stock_quantity")[:15]),
                    "pending_orders": orders.filter(status="pending").count(),
                    "today_orders": orders.filter(created_at__date=timezone.localdate()).count(),
                    "revenue_recorded": str(orders.exclude(status="cancelled").aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")),
                    "mpesa_pending": payments.filter(method="mpesa", status="pending").count(),
                    "mpesa_paid": payments.filter(method="mpesa", status="paid").count(),
                    "mpesa_failed": payments.filter(method="mpesa", status="failed").count(),
                    "recent_payments": list(
                        payments.order_by("-created_at").values(
                            "id", "order_id", "status", "amount", "provider_reference", "created_at"
                        )[:12]
                    ),
                }
                prompt = f"""
You are Shopiva Kenya's admin intelligence assistant.
Answer the administrator's question using ONLY this database snapshot.
Be concise and actionable. Do not invent facts.
For M-PESA, never call a payment successful unless its recorded status is exactly 'paid'.
Pending means awaiting confirmed provider data. Failed means failed.
If data is insufficient, say so clearly.
Database snapshot: {json.dumps(snapshot, default=str)}
Administrator question: {question}
"""
                response = OpenAI(api_key=api_key).responses.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
                    input=prompt,
                )
                return JsonResponse({"answer": response.output_text.strip(), "ai": True})
            except Exception:
                pass

        if not question:
            answer = "Please type a question. I can help with products, orders, stock, revenue and delivery operations."
        elif any(word in question for word in ("delivery", "rider", "agent")) and any(word in question for word in ("how many", "count", "online", "active")):
            answer = f"Shopiva has {agents.filter(status__in=['available', 'on_delivery']).count()} active delivery agent(s)."
        elif any(word in question for word in ("low stock", "low-stock", "stock")):
            low = products.filter(stock_quantity__lte=5, is_active=True).order_by("stock_quantity")[:10]
            answer = (
                "Low-stock products:\n" + "\n".join(f"• {p.name}: {p.stock_quantity} units" for p in low)
                if low
                else "Good news — there are currently no active products at or below 5 units of stock."
            )
        elif any(word in question for word in ("pending", "awaiting")) and "order" in question:
            answer = f"There are {orders.filter(status='pending').count()} pending order(s) waiting for attention."
        elif any(word in question for word in ("today", "today's")) and "order" in question:
            answer = f"Shopiva has received {orders.filter(created_at__date=timezone.localdate()).count()} order(s) today."
        elif any(word in question for word in ("failed", "attention", "problem")) and any(word in question for word in ("payment", "mpesa", "m-pesa")):
            failed = payments.filter(method="mpesa", status="failed").order_by("-created_at")[:8]
            pending = payments.filter(method="mpesa", status="pending").order_by("-created_at")[:8]
            answer = (
                f"M-PESA needs attention: {failed.count()} failed transaction(s) in the latest set and {pending.count()} transaction(s) still pending."
                if failed or pending
                else "No failed or pending M-PESA transactions are currently recorded."
            )
        elif any(word in question for word in ("pending", "waiting")) and any(word in question for word in ("payment", "mpesa", "m-pesa")):
            pending = payments.filter(method="mpesa", status="pending").count()
            answer = f"There are {pending} M-PESA transaction(s) awaiting confirmed provider results. Pending does not mean paid."
        elif any(word in question for word in ("failed", "failure")) and any(word in question for word in ("payment", "mpesa", "m-pesa")):
            failed = payments.filter(method="mpesa", status="failed").count()
            answer = f"There are {failed} recorded failed M-PESA transaction(s)."
        elif any(word in question for word in ("revenue", "sales", "income")):
            revenue = orders.exclude(status="cancelled").aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")
            answer = f"Current recorded revenue excluding cancelled orders is KSh {revenue:,.2f}."
        elif any(word in question for word in ("product", "products")) and any(word in question for word in ("how many", "count", "total")):
            answer = f"Shopiva currently has {products.count()} product(s), with {products.filter(is_active=True).count()} active."
        elif "help" in question or "what can" in question:
            answer = "I can answer questions about product counts, low stock, pending orders, today's orders, revenue and delivery operations."
        else:
            answer = "Try: 'How many products do we have?', 'Which products are low stock?', 'How many pending orders?', or 'How many delivery riders are active?', 'Are there any M-PESA payments needing attention?', or 'How many M-PESA payments are pending?'"

        return JsonResponse({"answer": answer})


shopiva_admin_site = ShopivaAdminSite(name="shopiva_admin")


@admin.register(Product, site=shopiva_admin_site)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "seller", "sku", "price", "discount_percent", "stock_quantity", "is_featured", "is_active")
    list_filter = ("is_featured", "is_active", "category")
    search_fields = ("name", "description", "sku")
    list_editable = ("discount_percent", "stock_quantity", "is_featured", "is_active")
    ordering = ("-id",)
    list_per_page = 25


@admin.register(Order, site=shopiva_admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "total_amount",
        "status",
        "payment_status",
        "delivery_agent",
        "tracking_code",
        "created_at",
    )
    list_filter = ("status", "payment_status", "delivery_agent", "created_at")
    search_fields = ("customer_name", "email", "phone", "address", "tracking_code", "payment_reference")
    ordering = ("-created_at",)
    list_per_page = 25
    readonly_fields = ("tracking_code", "packed_at", "paid_at", "assigned_at")

    def save_model(self, request, obj, form, change):
        previous = None
        if change and obj.pk:
            previous = Order.objects.get(pk=obj.pk)

        if not obj.tracking_code:
            obj.tracking_code = f"SPV-{uuid.uuid4().hex[:10].upper()}"

        now = timezone.now()
        if obj.status == "packed" and not obj.packed_at:
            obj.packed_at = now
        if obj.payment_status == "paid" and not obj.paid_at:
            obj.paid_at = now
        if obj.delivery_agent_id and not obj.assigned_at:
            obj.assigned_at = now

        super().save_model(request, obj, form, change)

        if previous is None:
            OrderEvent.objects.create(
                order=obj,
                event_type="placed",
                note="Order created in the Shopiva control center.",
                actor=request.user,
            )
            return

        if previous.status != obj.status and obj.status == "delivered":
            for settlement in SellerSettlement.objects.select_for_update().filter(order=obj, status="pending"):
                wallet = SellerWallet.objects.select_for_update().get(seller=settlement.seller)
                wallet.pending_balance = max(Decimal("0.00"), wallet.pending_balance - settlement.seller_amount)
                wallet.available_balance += settlement.seller_amount
                wallet.save(update_fields=("pending_balance", "available_balance", "updated_at"))
                settlement.status = "available"
                settlement.released_at = now
                settlement.save(update_fields=("status", "released_at"))
        if previous.status != obj.status:
            event_map = {
                "confirmed": "confirmed",
                "packed": "packed",
                "processing": "processing",
                "shipped": "shipped",
                "out_for_delivery": "out_for_delivery",
                "delivered": "delivered",
                "cancelled": "cancelled",
            }
            event_type = event_map.get(obj.status)
            if event_type:
                OrderEvent.objects.create(
                    order=obj,
                    event_type=event_type,
                    note=f"Order status changed to {obj.get_status_display()}.",
                    actor=request.user,
                    delivery_agent=obj.delivery_agent,
                )

        if previous.payment_status != obj.payment_status and obj.payment_status == "paid":
            OrderEvent.objects.create(
                order=obj,
                event_type="paid",
                note=f"Payment confirmed{(' - ' + obj.payment_reference) if obj.payment_reference else ''}.",
                actor=request.user,
                delivery_agent=obj.delivery_agent,
            )

        if previous.delivery_agent_id != obj.delivery_agent_id and obj.delivery_agent:
            OrderEvent.objects.create(
                order=obj,
                event_type="assigned",
                note=f"Assigned to {obj.delivery_agent.display_name}.",
                actor=request.user,
                delivery_agent=obj.delivery_agent,
            )


@admin.register(OrderItem, site=shopiva_admin_site)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "price")
    search_fields = ("product__name",)
    ordering = ("-id",)
    list_per_page = 25


@admin.register(DeliveryAgent, site=shopiva_admin_site)
class DeliveryAgentAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "phone",
        "vehicle_type",
        "vehicle_number",
        "status",
        "is_active",
        "last_location_at",
    )
    list_filter = ("status", "is_active", "vehicle_type")
    search_fields = ("user__username", "user__first_name", "user__last_name", "phone", "vehicle_number")
    list_editable = ("status", "is_active")
    readonly_fields = ("current_latitude", "current_longitude", "last_location_at")
    list_per_page = 25


@admin.register(CustomerAddress, site=shopiva_admin_site)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ("label", "full_name", "phone", "town", "county", "is_default", "user")
    list_filter = ("county", "is_default")
    search_fields = ("full_name", "phone", "town", "county", "address_line", "user__username", "user__email")
    list_editable = ("is_default",)


@admin.register(WishlistItem, site=shopiva_admin_site)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__username", "user__email", "product__name")
    ordering = ("-created_at",)


@admin.register(OrderEvent, site=shopiva_admin_site)
class OrderEventAdmin(admin.ModelAdmin):
    list_display = ("order", "event_type", "delivery_agent", "actor", "created_at")
    list_filter = ("event_type", "delivery_agent", "created_at")
    search_fields = ("order__customer_name", "order__tracking_code", "note", "actor__username")
    readonly_fields = ("order", "event_type", "note", "actor", "delivery_agent", "created_at")
    ordering = ("-created_at",)


@admin.register(User, site=shopiva_admin_site)
class ShopivaUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_staff", "is_active", "date_joined")
    search_fields = ("username", "email")
    list_filter = ("is_staff", "is_active", "is_superuser")


@admin.register(Group, site=shopiva_admin_site)
class ShopivaGroupAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(SellerProfile, site=shopiva_admin_site)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ("business_name", "user", "mpesa_phone", "commission_percent", "is_active", "created_at")
    list_filter = ("is_active", "commission_percent")
    search_fields = ("business_name", "user__username", "user__email", "mpesa_phone")
    list_editable = ("commission_percent", "is_active")

@admin.register(SellerWallet, site=shopiva_admin_site)
class SellerWalletAdmin(admin.ModelAdmin):
    list_display = ("seller", "pending_balance", "available_balance", "total_sales", "total_commission", "updated_at")
    search_fields = ("seller__business_name", "seller__user__username", "seller__user__email")
    readonly_fields = ("pending_balance", "available_balance", "total_sales", "total_commission", "updated_at")

@admin.register(SellerSettlement, site=shopiva_admin_site)
class SellerSettlementAdmin(admin.ModelAdmin):
    list_display = ("order", "seller", "gross_amount", "platform_commission", "seller_amount", "status", "provider_reference", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order__tracking_code", "seller__business_name", "seller__user__username", "provider_reference")
    readonly_fields = ("order", "seller", "gross_amount", "platform_commission", "seller_amount", "provider_reference", "created_at", "released_at", "paid_at")
