from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone

from .models import Order, OrderItem, Product


class ShopivaAdminSite(admin.AdminSite):
    site_header = "Shopiva Control Center"
    site_title = "Shopiva Admin"
    index_title = "Store Operations"
    index_template = "admin/index.html"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        today = timezone.localdate()
        orders = Order.objects.all()
        products = Product.objects.all()

        extra_context.update(
            {
                "shopiva_stats": {
                    "products": products.count(),
                    "active_products": products.filter(is_active=True).count(),
                    "low_stock": products.filter(stock_quantity__lte=5, is_active=True).count(),
                    "orders": orders.count(),
                    "pending_orders": orders.filter(status="pending").count(),
                    "today_orders": orders.filter(created_at__date=today).count(),
                    "revenue": sum(
                        (order.total_amount for order in orders.exclude(status="cancelled")),
                        0,
                    ),
                },
                "recent_orders": orders.select_related().order_by("-created_at")[:8],
                "low_stock_products": products.filter(
                    stock_quantity__lte=5, is_active=True
                ).order_by("stock_quantity", "name")[:8],
                "recent_products": products.order_by("-id")[:6],
            }
        )
        return super().index(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "ai-assistant/",
                self.admin_view(self.ai_assistant),
                name="ai_assistant",
            ),
        ]
        return custom_urls + urls

    def ai_assistant(self, request):
        if request.method != "POST":
            return JsonResponse({"answer": "Ask me about products, orders, stock, revenue, or Shopiva operations."})

        question = request.POST.get("question", "").strip().lower()
        products = Product.objects.all()
        orders = Order.objects.all()

        if not question:
            answer = "Please type a question. I can help with products, orders, stock, revenue and store activity."
        elif any(word in question for word in ("low stock", "low-stock", "stock")):
            low = products.filter(stock_quantity__lte=5, is_active=True).order_by("stock_quantity")[:10]
            if low:
                answer = "Low-stock products:\n" + "\n".join(
                    f"• {p.name}: {p.stock_quantity} units" for p in low
                )
            else:
                answer = "Good news — there are currently no active products at or below 5 units of stock."
        elif any(word in question for word in ("pending", "awaiting")) and "order" in question:
            count = orders.filter(status="pending").count()
            answer = f"There are {count} pending order(s) waiting for attention."
        elif any(word in question for word in ("today", "today's")) and "order" in question:
            count = orders.filter(created_at__date=timezone.localdate()).count()
            answer = f"Shopiva has received {count} order(s) today."
        elif any(word in question for word in ("revenue", "sales", "income")):
            revenue = sum(
                (order.total_amount for order in orders.exclude(status="cancelled")),
                0,
            )
            answer = f"Current recorded revenue excluding cancelled orders is KSh {revenue:,.2f}."
        elif any(word in question for word in ("product", "products")) and any(
            word in question for word in ("how many", "count", "total")
        ):
            answer = f"Shopiva currently has {products.count()} product(s), with {products.filter(is_active=True).count()} active."
        elif "help" in question or "what can" in question:
            answer = (
                "I can answer questions about:\n"
                "• product counts and active products\n"
                "• low-stock products\n"
                "• pending orders\n"
                "• today's orders\n"
                "• recorded revenue\n"
                "• basic Shopiva operations"
            )
        else:
            answer = (
                "I can help with Shopiva's live database information. Try: "
                "'How many products do we have?', 'Which products are low stock?', "
                "'How many pending orders?', or 'What is our revenue?'"
            )

        return JsonResponse({"answer": answer})


shopiva_admin_site = ShopivaAdminSite(name="shopiva_admin")


@admin.register(Product, site=shopiva_admin_site)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "price",
        "discount_percent",
        "stock_quantity",
        "is_featured",
        "is_active",
    )
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
        "email",
        "phone",
        "total_amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("customer_name", "email", "phone", "address")
    ordering = ("-created_at",)
    list_per_page = 25


@admin.register(OrderItem, site=shopiva_admin_site)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "price")
    search_fields = ("product__name",)
    ordering = ("-id",)
    list_per_page = 25


@admin.register(User, site=shopiva_admin_site)
class ShopivaUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_staff", "is_active", "date_joined")
    search_fields = ("username", "email")
    list_filter = ("is_staff", "is_active", "is_superuser")


@admin.register(Group, site=shopiva_admin_site)
class ShopivaGroupAdmin(admin.ModelAdmin):
    search_fields = ("name",)
