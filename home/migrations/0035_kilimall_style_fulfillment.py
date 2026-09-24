from django.db import migrations, models
import django.db.models.deletion


def seed_pickup_point(apps, schema_editor):
    DeliveryHub = apps.get_model("home", "DeliveryHub")
    DeliveryPickupPoint = apps.get_model("home", "DeliveryPickupPoint")
    hub = DeliveryHub.objects.filter(code="ELD-HQ").first()
    if hub:
        DeliveryPickupPoint.objects.update_or_create(
            code="ELD-HQ-PICKUP",
            defaults={
                "name": "Shopiva Eldoret HQ Pickup",
                "county": hub.county,
                "town": hub.town,
                "address": hub.address,
                "latitude": hub.latitude,
                "longitude": hub.longitude,
                "partner_name": "Shopiva",
                "is_active": True,
                "max_holding_days": 7,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("home", "0034_fulfillment_hubs_distance_pricing")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="package_class",
            field=models.CharField(
                choices=[("micro", "Micro"), ("small", "Small"), ("medium", "Medium"), ("big", "Big"), ("extra_big", "Extra Big")],
                default="small",
                max_length=20,
            ),
        ),
        migrations.AddField(model_name="product", name="shipping_weight_kg", field=models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True)),
        migrations.AddField(model_name="product", name="package_length_cm", field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
        migrations.AddField(model_name="product", name="package_width_cm", field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
        migrations.AddField(model_name="product", name="package_height_cm", field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
        migrations.AddField(model_name="product", name="fulfillment_ready", field=models.BooleanField(default=True, help_text="Seller has supplied the shipping data required for platform fulfillment.")),
        migrations.CreateModel(
            name="DeliveryPickupPoint",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("code", models.CharField(max_length=40, unique=True)),
                ("county", models.CharField(max_length=100)),
                ("town", models.CharField(max_length=120)),
                ("address", models.CharField(max_length=255)),
                ("latitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("longitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("partner_name", models.CharField(blank=True, max_length=150)),
                ("is_active", models.BooleanField(default=True)),
                ("max_holding_days", models.PositiveSmallIntegerField(default=7)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("county", "town", "name")},
        ),
        migrations.CreateModel(
            name="DeliveryRateCard",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("fulfillment_model", models.CharField(choices=[("shopiva_owned", "Shopiva-owned fleet"), ("third_party", "Third-party couriers"), ("independent", "Independent riders/drivers"), ("mixed", "Mixed fulfillment")], default="mixed", max_length=30)),
                ("delivery_mode", models.CharField(choices=[("standard", "Standard Delivery"), ("pickup", "Pickup Station"), ("express", "Express Delivery")], default="standard", max_length=20)),
                ("package_class", models.CharField(choices=[("micro", "Micro"), ("small", "Small"), ("medium", "Medium"), ("big", "Big"), ("extra_big", "Extra Big")], default="small", max_length=20)),
                ("route_class", models.CharField(choices=[("local", "Local"), ("regional", "Regional"), ("national", "National"), ("remote", "Remote / Rural")], default="local", max_length=20)),
                ("base_fee", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("per_km_fee", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("per_extra_seller_fee", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("minimum_fee", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("maximum_fee", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("rounding_step", models.DecimalField(decimal_places=2, default=10, max_digits=10)),
                ("is_active", models.BooleanField(default=False)),
                ("notes", models.TextField(blank=True, help_text="Document the approved courier/platform rate basis before activation.")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("delivery_mode", "package_class", "route_class", "name")},
        ),
        migrations.RunPython(seed_pickup_point, migrations.RunPython.noop),
    ]
