from django.conf import settings
from django.db import migrations, models
import cloudinary.models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0012_payout_inventory_safeguards"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="image",
            field=cloudinary.models.CloudinaryField(
                blank=True,
                max_length=255,
                null=True,
                folder="shopiva/products",
                verbose_name="image",
            ),
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("notification_type", models.CharField(choices=[("order", "Order"), ("payment", "Payment"), ("delivery", "Delivery"), ("payout", "Payout"), ("system", "System")], default="system", max_length=20)),
                ("title", models.CharField(max_length=160)),
                ("message", models.TextField()),
                ("link", models.CharField(blank=True, max_length=255)),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="shopiva_notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="ProductReview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rating", models.PositiveSmallIntegerField()),
                ("comment", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("customer", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="shopiva_reviews", to=settings.AUTH_USER_MODEL)),
                ("order", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="product_reviews", to="home.order")),
                ("product", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="reviews", to="home.product")),
            ],
            options={
                "ordering": ("-created_at",),
                "constraints": [models.UniqueConstraint(fields=("product", "customer", "order"), name="unique_product_review_per_order")],
            },
        ),
    ]
