from django.db import migrations, models
import cloudinary.models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0024_cleanup_legacy_repair_constraints"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductMedia",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "image",
                    cloudinary.models.CloudinaryField(
                        folder="shopiva/product-media",
                        max_length=255,
                        verbose_name="image",
                    ),
                ),
                (
                    "position",
                    models.PositiveSmallIntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(7),
                        ],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="media",
                        to="home.product",
                    ),
                ),
            ],
            options={
                "ordering": ("position", "created_at"),
                "constraints": [
                    models.UniqueConstraint(
                        fields=("product", "position"),
                        name="unique_product_media_position",
                    ),
                ],
            },
        ),
    ]
