from django.conf import settings
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from cloudinary.models import CloudinaryField


class SellerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seller_profile")
    business_name = models.CharField(max_length=200, blank=True)
    mpesa_phone = models.CharField(max_length=30, blank=True)
    business_address = models.CharField(max_length=255, blank=True, default="")
    business_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    business_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    commission_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10,
        help_text="Shopiva platform commission. Sellers cannot set or change this rate.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.commission_percent = Decimal("10.00")
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.business_name or self.user.get_full_name() or self.user.username


class SellerWallet(models.Model):
    seller = models.OneToOneField(SellerProfile, on_delete=models.CASCADE, related_name="wallet")
    pending_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    available_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(pending_balance__gte=0), name="sellerwallet_pending_gte_0"),
            models.CheckConstraint(condition=models.Q(available_balance__gte=0), name="sellerwallet_available_gte_0"),
            models.CheckConstraint(condition=models.Q(total_sales__gte=0), name="sellerwallet_sales_gte_0"),
            models.CheckConstraint(condition=models.Q(total_commission__gte=0), name="sellerwallet_commission_gte_0"),
        ]

    def __str__(self):
        return f"{self.seller} wallet"


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=64, unique=True, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=100, blank=True, default="General")
    image = CloudinaryField("image", folder="shopiva/products", blank=True, null=True)
    discount_percent = models.PositiveIntegerField(default=0)
    promo_text = models.CharField(max_length=120, blank=True)
    is_featured = models.BooleanField(default=False)
    seller = models.ForeignKey(SellerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")

    @property
    def discounted_price(self):
        discount = Decimal(self.discount_percent or 0)
        return self.price * (Decimal("100") - discount) / Decimal("100")

    @property
    def has_discount(self):
        return (self.discount_percent or 0) > 0

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        from django.db.models import Avg
        return self.reviews.aggregate(value=Avg("rating"))["value"] or 0

    @property
    def review_count(self):
        return self.reviews.count()

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gt=0), name="product_price_gt_0"),
            models.CheckConstraint(condition=models.Q(discount_percent__gte=0, discount_percent__lte=100), name="product_discount_0_100"),
        ]


class DeliveryAgent(models.Model):
    STATUS_CHOICES = [("offline", "Offline"), ("available", "Available"), ("on_delivery", "On Delivery")]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="delivery_agent_profile")
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
    STATUS_CHOICES = [("pending", "Placed / Pending"), ("confirmed", "Confirmed"), ("paid", "Paid"), ("packed", "Packed"), ("processing", "Processing"), ("shipped", "Shipped"), ("out_for_delivery", "Out for Delivery"), ("delivered", "Delivered"), ("cancelled", "Cancelled")]
    PAYMENT_STATUS_CHOICES = [("unpaid", "Unpaid"), ("pending", "Payment Pending"), ("paid", "Paid"), ("failed", "Failed"), ("refunded", "Refunded")]
    customer_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address = models.TextField()
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="unpaid")
    payment_reference = models.CharField(max_length=120, blank=True)
    tracking_code = models.CharField(max_length=40, unique=True, null=True, blank=True)
    delivery_agent = models.ForeignKey(DeliveryAgent, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    packed_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(total_amount__gte=0), name="order_total_gte_0"),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    seller = models.ForeignKey(SellerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="order_items")
    seller_gross = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    platform_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    seller_net = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gt=0), name="orderitem_quantity_gt_0"),
            models.CheckConstraint(condition=models.Q(price__gte=0), name="orderitem_price_gte_0"),
            models.CheckConstraint(condition=models.Q(seller_gross__gte=0), name="orderitem_gross_gte_0"),
            models.CheckConstraint(condition=models.Q(platform_commission__gte=0), name="orderitem_commission_gte_0"),
            models.CheckConstraint(condition=models.Q(seller_net__gte=0), name="orderitem_net_gte_0"),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class OrderEvent(models.Model):
    EVENT_CHOICES = [("placed", "Order Placed"), ("confirmed", "Order Confirmed"), ("payment_pending", "Payment Pending"), ("paid", "Payment Confirmed"), ("packed", "Order Packed"), ("assigned", "Delivery Agent Assigned"), ("processing", "Processing"), ("shipped", "Shipped"), ("out_for_delivery", "Out for Delivery"), ("delivered", "Delivered"), ("cancelled", "Order Cancelled")]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES)
    note = models.CharField(max_length=255, blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="shopiva_order_events")
    delivery_agent = models.ForeignKey(DeliveryAgent, on_delete=models.SET_NULL, null=True, blank=True, related_name="order_events")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Order #{self.order_id} - {self.get_event_type_display()}"


class DeliveryLocationPing(models.Model):
    agent = models.ForeignKey(DeliveryAgent, on_delete=models.CASCADE, related_name="location_history")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy_meters = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    speed_mps = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    heading_degrees = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-recorded_at",)
        indexes = [models.Index(fields=("agent", "-recorded_at"))]
        constraints = [
            models.CheckConstraint(condition=models.Q(latitude__gte=-90, latitude__lte=90), name="deliveryping_latitude_range"),
            models.CheckConstraint(condition=models.Q(longitude__gte=-180, longitude__lte=180), name="deliveryping_longitude_range"),
            models.CheckConstraint(condition=models.Q(accuracy_meters__gte=0) | models.Q(accuracy_meters__isnull=True), name="deliveryping_accuracy_gte_0"),
            models.CheckConstraint(condition=models.Q(speed_mps__gte=0) | models.Q(speed_mps__isnull=True), name="deliveryping_speed_gte_0"),
        ]

    def __str__(self):
        return f"{self.agent.display_name} @ {self.recorded_at:%Y-%m-%d %H:%M:%S}"


class PaymentTransaction(models.Model):
    METHOD_CHOICES = [("mpesa", "M-PESA"), ("card", "Card"), ("cod", "Cash on Delivery")]
    STATUS_CHOICES = [("initiated", "Initiated"), ("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed"), ("cancelled", "Cancelled"), ("refunded", "Refunded")]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="initiated")
    provider = models.CharField(max_length=40, default="shopiva")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    phone = models.CharField(max_length=30, blank=True)
    merchant_request_id = models.CharField(max_length=120, blank=True, db_index=True)
    checkout_request_id = models.CharField(max_length=120, blank=True, db_index=True)
    provider_reference = models.CharField(max_length=120, blank=True, db_index=True)
    idempotency_key = models.CharField(max_length=120, unique=True)
    raw_response = models.JSONField(default=dict, blank=True)
    inventory_released = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("order", "status"))]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="payment_amount_gt_0"),
        ]

    def __str__(self):
        return f"{self.method.upper()} #{self.id} - Order #{self.order_id}"


class CustomerAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shopiva_addresses")
    label = models.CharField(max_length=80, default="Home")
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    county = models.CharField(max_length=100)
    town = models.CharField(max_length=100)
    address_line = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-is_default", "-created_at")
        constraints = [
            models.UniqueConstraint(fields=("user",), condition=models.Q(is_default=True), name="unique_default_shopiva_address"),
        ]

    def __str__(self):
        return f"{self.label} - {self.town}, {self.county}"


class WishlistItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shopiva_wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlist_items")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [models.UniqueConstraint(fields=("user", "product"), name="unique_shopiva_wishlist_item")]

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class SellerPayoutRequest(models.Model):
    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("processing", "Processing"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]
    seller = models.ForeignKey(SellerProfile, on_delete=models.PROTECT, related_name="payout_requests")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    phone = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="requested")
    provider_reference = models.CharField(max_length=120, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    failure_reason = models.CharField(max_length=255, blank=True)
    idempotency_key = models.CharField(max_length=120, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="sellerpayout_amount_gt_0"),
        ]

    def __str__(self):
        return f"Payout #{self.id} - {self.seller} - KSh {self.amount}"


class SellerSettlement(models.Model):
    STATUS_CHOICES = [("pending", "Pending delivery"), ("available", "Available for payout"), ("paid", "Paid to seller"), ("held", "Held"), ("refunded", "Refunded")]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="seller_settlements")
    seller = models.ForeignKey(SellerProfile, on_delete=models.PROTECT, related_name="settlements")
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    platform_commission = models.DecimalField(max_digits=12, decimal_places=2)
    seller_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    provider_reference = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(fields=("order", "seller"), name="unique_order_seller_settlement"),
            models.CheckConstraint(condition=models.Q(gross_amount__gte=0), name="settlement_gross_gte_0"),
            models.CheckConstraint(condition=models.Q(platform_commission__gte=0), name="settlement_commission_gte_0"),
            models.CheckConstraint(condition=models.Q(seller_amount__gte=0), name="settlement_seller_gte_0"),
        ]

    def __str__(self):
        return f"Settlement #{self.id} - Order #{self.order_id}"


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shopiva_reviews")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="product_reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(fields=("product", "customer", "order"), name="unique_product_review_per_order"),
            models.CheckConstraint(condition=models.Q(rating__gte=1, rating__lte=5), name="productreview_rating_1_5"),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.rating}/5"


class Notification(models.Model):
    TYPE_CHOICES = [("order", "Order"), ("payment", "Payment"), ("delivery", "Delivery"), ("payout", "Payout"), ("system", "System")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shopiva_notifications")
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="system")
    title = models.CharField(max_length=160)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user.username}: {self.title}"


class NotificationDelivery(models.Model):
    CHANNEL_CHOICES = (
        ("email", "Email"),
        ("sms", "SMS"),
        ("whatsapp", "WhatsApp"),
    )
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted by provider"),
        ("delivered", "Delivered"),
        ("failed", "Failed"),
        ("skipped", "Skipped"),
    )
    notification = models.ForeignKey("Notification", on_delete=models.CASCADE, related_name="deliveries")
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    provider_message_id = models.CharField(max_length=160, blank=True)
    provider_status = models.CharField(max_length=120, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [models.UniqueConstraint(fields=("notification", "channel"), name="unique_notification_delivery_channel")]

    def __str__(self):
        return f"{self.notification_id} · {self.channel} · {self.status}"
