from django.contrib import admin
from .models import Product, Order, OrderItem


@admin.register(Product)
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
    list_filter = (
        "is_featured",
        "is_active",
        "category",
    )
    search_fields = (
        "name",
        "description",
        "sku",
    )
    list_editable = (
        "discount_percent",
        "stock_quantity",
        "is_featured",
        "is_active",
    )
    ordering = ("-id",)


@admin.register(Order)
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
    list_filter = (
        "status",
        "created_at",
    )
    search_fields = (
        "customer_name",
        "email",
        "phone",
        "address",
    )
    ordering = ("-created_at",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price",
    )
    search_fields = (
        "product__name",
    )
    ordering = ("-id",)
