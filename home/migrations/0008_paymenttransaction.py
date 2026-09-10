from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("home", "0007_deliverylocationping")]

    operations = [
        migrations.CreateModel(
            name="PaymentTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("method", models.CharField(choices=[("mpesa", "M-PESA"), ("card", "Card"), ("cod", "Cash on Delivery")], max_length=20)),
                ("status", models.CharField(choices=[("initiated", "Initiated"), ("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed"), ("cancelled", "Cancelled"), ("refunded", "Refunded")], default="initiated", max_length=20)),
                ("provider", models.CharField(default="shopiva", max_length=40)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("merchant_request_id", models.CharField(blank=True, db_index=True, max_length=120)),
                ("checkout_request_id", models.CharField(blank=True, db_index=True, max_length=120)),
                ("provider_reference", models.CharField(blank=True, db_index=True, max_length=120)),
                ("idempotency_key", models.CharField(max_length=120, unique=True)),
                ("raw_response", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to="home.order")),
            ],
            options={"ordering": ("-created_at",), "indexes": [models.Index(fields=["order", "status"], name="home_paym_order_i_1a2c7d_idx")]},
        ),
    ]
