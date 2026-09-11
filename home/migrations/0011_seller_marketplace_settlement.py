from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0010_customeraddress_wishlistitem"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SellerProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("business_name", models.CharField(blank=True, max_length=200)),
                ("mpesa_phone", models.CharField(blank=True, max_length=30)),
                ("commission_percent", models.DecimalField(decimal_places=2, default=10, max_digits=5)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="seller_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="SellerWallet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("pending_balance", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("available_balance", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("total_sales", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("total_commission", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("seller", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="wallet", to="home.sellerprofile")),
            ],
        ),
        migrations.AddField(
            model_name="product",
            name="seller",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="products", to="home.sellerprofile"),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="seller",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="order_items", to="home.sellerprofile"),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="seller_gross",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="platform_commission",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="seller_net",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.CreateModel(
            name="SellerSettlement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("gross_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("platform_commission", models.DecimalField(decimal_places=2, max_digits=12)),
                ("seller_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("status", models.CharField(choices=[("pending", "Pending delivery"), ("available", "Available for payout"), ("paid", "Paid to seller"), ("held", "Held"), ("refunded", "Refunded")], default="pending", max_length=20)),
                ("provider_reference", models.CharField(blank=True, max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("released_at", models.DateTimeField(blank=True, null=True)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="seller_settlements", to="home.order")),
                ("seller", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="settlements", to="home.sellerprofile")),
            ],
            options={"ordering": ("-created_at",)},
            constraints=[models.UniqueConstraint(fields=("order", "seller"), name="unique_order_seller_settlement")],
        ),
    ]
