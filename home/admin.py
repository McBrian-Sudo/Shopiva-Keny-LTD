from decimal import Decimal

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User
from django.db.models import ProtectedError, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone

from .models import Order, OrderItem, Product


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
                    "revenue": orders.exclude(status="cancelled").aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00"),
                },
                "recent_orders": orders.order_by("-created_at")[:8],
                "low_stock_products": products.filter(stock_quantity__lte=5, is_active=True).order_by("stock_quantity", "name")[:8],
                "recent_products": products.order_by("-id")[:6],
            }
        )
        return super().index(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("products/", self.admin_view(self.product_manager), name="product_manager"),
            path("products/add/", self.admin_view(self.product_add), name="product_add"),
            path("products/<int:product_id>/edit/", self.admin_view(self.product_edit), name="product_edit"),
            path("products/<int:product_id>/delete/", self.admin_view(self.product_delete), name="product_delete"),
            path("ai-assistant/", self.admin_view(self.ai_assistant), name="ai_assistant"),
        ]
        return custom_urls + urls

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
            return JsonResponse({"answer": "Ask me about products, orders, stock, revenue, or Shopiva operations."})

        question = request.POST.get("question", "").strip().lower()
        products = Product.objects.all()
        orders = Order.objects.all()

        if not question:
            answer = "Please type a question. I can help with products, orders, stock, revenue and store activity."
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
        elif any(word in question for word in ("revenue", "sales", "income")):
            revenue = orders.exclude(status="cancelled").aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")
            answer = f"Current recorded revenue excluding cancelled orders is KSh {revenue:,.2f}."
        elif any(word in question for word in ("product", "products")) and any(word in question for word in ("how many", "count", "total")):
            answer = f"Shopiva currently has {products.count()} product(s), with {products.filter(is_active=True).count()} active."
        elif "help" in question or "what can" in question:
            answer = "I can answer questions about product counts, low stock, pending orders, today's orders, revenue and basic Shopiva operations."
        else:
            answer = "Try: 'How many products do we have?', 'Which products are low stock?', 'How many pending orders?', or 'What is our revenue?'"

        return JsonResponse({"answer": answer})


shopiva_admin_site = ShopivaAdminSite(name="shopiva_admin")


@admin.register(Product, site=shopiva_admin_site)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "price", "discount_percent", "stock_quantity", "is_featured", "is_active")
    list_filter = ("is_featured", "is_active", "category")
    search_fields = ("name", "description", "sku")
    list_editable = ("discount_percent", "stock_quantity", "is_featured", "is_active")
    ordering = ("-id",)
    list_per_page = 25


@admin.register(Order, site=shopiva_admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "email", "phone", "total_amount", "status", "created_at")
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
