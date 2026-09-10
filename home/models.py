from django.conf import settings
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=64, unique=True, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=100, blank=True, default="General")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    discount_percent = models.PositiveIntegerField(default=0)
    promo_text = models.CharField(max_length=120, blank=True)
    is_featured = models.BooleanField(default=False)

    @property
    def discounted_price(self):
        from decimal import Decimal

        discount = Decimal(self.discount_percent or 0)
        return self.price * (Decimal("100") - discount) / Decimal("100")

    @property
    def has_discount(self):
        return (self.discount_percent or 0) > 0

    def __str__(self):
        return self.name


class DeliveryAgent(models.Model):
    STATUS_CHOICES = [
        ("offline", "Offline"),
        ("available", "Available"),
        ("on_delivery", "On Delivery"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="delivery_agent_profile",
    )
    phone = models.CharField(max_length=30, blank=True)
    vehicle_type = models.CharField(max_length=80, blank=True)
    vehicle_number = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="offline")
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def location_is_live(self):
        from django.utils import timezone

        if not self.last_location_at:
            return False
        return (timezone.now() - self.last_location_at).total_seconds() <= 90

    def __str__(self):
        return self.display_name


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Placed / Pending"),
        ("confirmed", "Confirmed"),
        ("paid", "Paid"),
        ("packed", "Packed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("pending", "Payment Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    customer_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address = models.TextField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="unpaid")
    payment_reference = models.CharField(max_length=120, blank=True)
    tracking_code = models.CharField(max_length=40, unique=True, null=True, blank=True)
    delivery_agent = models.ForeignKey(
        DeliveryAgent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    packed_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class OrderEvent(models.Model):
    EVENT_CHOICES = [
        ("placed", "Order Placed"),
        ("confirmed", "Order Confirmed"),
        ("payment_pending", "Payment Pending"),
        ("paid", "Payment Confirmed"),
        ("packed", "Order Packed"),
        ("assigned", "Delivery Agent Assigned"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Order Cancelled"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES)
    note = models.CharField(max_length=255, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shopiva_order_events",
    )
    delivery_agent = models.ForeignKey(
        DeliveryAgent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Order #{self.order_id} - {self.get_event_type_display()}"


class DeliveryLocationPing(models.Model):
    """Timestamped GPS sample shared by a delivery partner."""

    agent = models.ForeignKey(
        DeliveryAgent,
        on_delete=models.CASCADE,
        related_name="location_history",
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy_meters = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    speed_mps = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    heading_degrees = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-recorded_at",)
        indexes = [
            models.Index(fields=("agent", "-recorded_at")),
        ]

    def __str__(self):
        return f"{self.agent.display_name} @ {self.recorded_at:%Y-%m-%d %H:%M:%S}"
