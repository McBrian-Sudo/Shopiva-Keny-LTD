from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0009_ensure_payment_status_column"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomerAddress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(default="Home", max_length=80)),
                ("full_name", models.CharField(max_length=200)),
                ("phone", models.CharField(max_length=30)),
                ("county", models.CharField(max_length=100)),
                ("town", models.CharField(max_length=100)),
                ("address_line", models.CharField(max_length=255)),
                ("landmark", models.CharField(blank=True, max_length=255)),
                ("is_default", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="shopiva_addresses", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-is_default", "-created_at")},
        ),
        migrations.CreateModel(
            name="WishlistItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="wishlist_items", to="home.product")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="shopiva_wishlist", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.AddConstraint(
            model_name="wishlistitem",
            constraint=models.UniqueConstraint(fields=("user", "product"), name="unique_shopiva_wishlist_item"),
        ),
    ]
