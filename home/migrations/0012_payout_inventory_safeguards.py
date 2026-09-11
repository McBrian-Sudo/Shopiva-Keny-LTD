from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0011_seller_marketplace_settlement"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymenttransaction",
            name="inventory_released",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="SellerPayoutRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("phone", models.CharField(max_length=30)),
                ("status", models.CharField(choices=[("requested", "Requested"), ("processing", "Processing"), ("paid", "Paid"), ("failed", "Failed"), ("cancelled", "Cancelled")], default="requested", max_length=20)),
                ("provider_reference", models.CharField(blank=True, max_length=120)),
                ("provider_response", models.JSONField(default=dict, blank=True)),
                ("failure_reason", models.CharField(blank=True, max_length=255)),
                ("idempotency_key", models.CharField(max_length=120, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("seller", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payout_requests", to="home.sellerprofile")),
            ],
            options={"ordering": ("-created_at",)},
        ),
    ]
