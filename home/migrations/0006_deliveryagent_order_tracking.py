# Generated for Shopiva delivery tracking and order history.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def seed_order_events(apps, schema_editor):
    Order = apps.get_model("home", "Order")
    OrderEvent = apps.get_model("home", "OrderEvent")

    for order in Order.objects.all().iterator():
        if not OrderEvent.objects.filter(order_id=order.pk).exists():
            OrderEvent.objects.create(
                order_id=order.pk,
                event_type="placed",
                note="Order history initialized from the existing order record.",
            )


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("home", "0005_product_is_active_product_sku_product_stock_quantity"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeliveryAgent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "phone",
                    models.CharField(blank=True, max_length=30),
                ),
                (
                    "vehicle_type",
                    models.CharField(blank=True, max_length=80),
                ),
                (
                    "vehicle_number",
                    models.CharField(blank=True, max_length=40),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("offline", "Offline"),
                            ("available", "Available"),
                            ("on_delivery", "On Delivery"),
                        ],
                        default="offline",
                        max_length=20,
                    ),
                ),
                (
                    "current_latitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        max_digits=9,
                        null=True,
                    ),
                ),
                (
                    "current_longitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        max_digits=9,
                        null=True,
                    ),
                ),
                (
                    "last_location_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="delivery_agent_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="order",
            name="assigned_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="packed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="paid_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_reference",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_status",
            field=models.CharField(
                choices=[
                    ("unpaid", "Unpaid"),
                    ("pending", "Payment Pending"),
                    ("paid", "Paid"),
                    ("failed", "Failed"),
                    ("refunded", "Refunded"),
                ],
                default="unpaid",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="tracking_code",
            field=models.CharField(blank=True, max_length=40, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_agent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="orders",
                to="home.deliveryagent",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Placed / Pending"),
                    ("confirmed", "Confirmed"),
                    ("paid", "Paid"),
                    ("packed", "Packed"),
                    ("processing", "Processing"),
                    ("shipped", "Shipped"),
                    ("out_for_delivery", "Out for Delivery"),
                    ("delivered", "Delivered"),
                    ("cancelled", "Cancelled"),
                ],
                default="pending",
                max_length=30,
            ),
        ),
        migrations.CreateModel(
            name="OrderEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "event_type",
                    models.CharField(
                        choices=[
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
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "note",
                    models.CharField(blank=True, max_length=255),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="shopiva_order_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "delivery_agent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="order_events",
                        to="home.deliveryagent",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="home.order",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.RunPython(seed_order_events, migrations.RunPython.noop),
    ]
