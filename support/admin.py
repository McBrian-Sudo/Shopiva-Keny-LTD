from django.contrib import admin

from .models import SupportMessage, SupportTicket


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "role", "priority", "status", "user", "updated_at")
    list_filter = ("role", "priority", "status")
    search_fields = ("subject", "category", "order_reference", "user__username", "user__email")
    readonly_fields = ("id", "created_at", "updated_at", "last_response_at")
    ordering = ("-updated_at",)


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ("ticket", "from_staff", "author", "created_at")
    list_filter = ("from_staff",)
    search_fields = ("body", "ticket__subject", "author__username", "author__email")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
