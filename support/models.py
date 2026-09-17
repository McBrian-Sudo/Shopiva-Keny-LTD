import uuid

from django.conf import settings
from django.db import models


class SupportTicket(models.Model):
    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("seller", "Seller"),
    )
    STATUS_CHOICES = (
        ("open", "Open"),
        ("in_progress", "In progress"),
        ("waiting_for_customer", "Waiting for customer"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    )
    PRIORITY_CHOICES = (
        ("normal", "Normal"),
        ("high", "High"),
        ("urgent", "Urgent"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shopiva_support_tickets",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    subject = models.CharField(max_length=160)
    category = models.CharField(max_length=80, default="General")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="normal")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="open")
    order_reference = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_response_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-updated_at",)
        indexes = [
            models.Index(fields=("user", "status")),
            models.Index(fields=("status", "priority", "updated_at")),
        ]

    def __str__(self):
        return f"{self.get_role_display()} · {self.subject}"


class SupportMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shopiva_support_messages",
    )
    body = models.TextField()
    from_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
        indexes = [models.Index(fields=("ticket", "created_at"))]

    def __str__(self):
        return f"Support message #{self.id}"
