from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


def seed_eldoret_fulfillment(apps, schema_editor):
    DeliveryHub = apps.get_model("home", "DeliveryHub")
    DeliveryPricingProfile = apps.get_model("home", "DeliveryPricingProfile")

    hub, _ = DeliveryHub.objects.update_or_create(
        code="ELD-HQ",
        defaults={
            "name": "Shopiva Eldoret Headquarters",
            "county": "Uasin Gishu",
            "town": "Eldoret",
            "address": "Eldoret, Uasin Gishu County, Kenya",
            "latitude": Decimal("0.520360"),
            "longitude": Decimal("35.269930"),
            "fulfillment_model": "mixed",
            "is_primary": True,
            "is_active": True,
        },
    )

    # The distance engine is deliberately not activated until Shopiva records
    # its approved transport economics. Existing destination tariffs remain the
    # customer-facing fallback during this configuration stage.
    DeliveryPricingProfile.objects.get_or_create(
        name="Eldoret HQ distance pricing — configure before activation",
        delivery_mode="standard",
        defaults={
            "pricing_mode": "distance",
            "base_fee": Decimal("0.00"),
            "per_km_fee": Decimal("0.00"),
            "per_seller_fee": Decimal("0.00"),
            "rural_surcharge": Decimal("0.00"),
            "minimum_fee": Decimal("0.00"),
            "maximum_fee": None,
            "rounding_step": Decimal("10.00"),
            "is_active": False,
            "notes": (
                "Configure from Shopiva's approved own-fleet, third-party, and "
                "independent courier costs. Do not activate with placeholder rates."
            ),
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0033_nationwide_county_coverage"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeliveryHub",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("code", models.CharField(max_length=30, unique=True)),
                ("county", models.CharField(max_length=100)),
                ("town", models.CharField(max_length=120)),
                ("address", models.CharField(blank=True, max_length=255)),
                ("latitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("longitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("fulfillment_model", models.CharField(choices=[
                    ("shopiva_owned", "Shopiva-owned fleet"),
                    ("third_party", "Third-party couriers"),
                    ("independent", "Independent riders/drivers"),
                    ("mixed", "Mixed fulfillment"),
                ], default="mixed", max_length=30)),
                ("is_primary", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("-is_primary", "name")},
        ),
        migrations.CreateModel(
            name="DeliveryPricingProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("delivery_mode", models.CharField(choices=[
                    ("standard", "Standard Delivery"),
                    ("pickup", "Pickup Station"),
                    ("express", "Express Delivery"),
                ], default="standard", max_length=20)),
                ("pricing_mode", models.CharField(choices=[
                    ("distance", "Distance-based pricing"),
                    ("legacy_tariff", "Destination tariff pricing"),
                ], default="distance", max_length=30)),
                ("base_fee", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("per_km_fee", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("per_seller_fee", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("rural_surcharge", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("minimum_fee", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("maximum_fee", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("rounding_step", models.DecimalField(decimal_places=2, default=10, max_digits=10)),
                ("is_active", models.BooleanField(default=False)),
                ("notes", models.TextField(blank=True, help_text="Record the approved commercial/transport basis for these rates.")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("delivery_mode", "name")},
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_hub",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="orders", to="home.deliveryhub"),
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_pricing_profile",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="orders", to="home.deliverypricingprofile"),
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_pricing_basis",
            field=models.CharField(default="legacy_tariff", max_length=40),
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_base_fee",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_distance_rate",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_distance_charge",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddConstraint(
            model_name="deliveryhub",
            constraint=models.CheckConstraint(condition=models.Q(("latitude__gte", -90), ("latitude__lte", 90)), name="deliveryhub_latitude_range"),
        ),
        migrations.AddConstraint(
            model_name="deliveryhub",
            constraint=models.CheckConstraint(condition=models.Q(("longitude__gte", -180), ("longitude__lte", 180)), name="deliveryhub_longitude_range"),
        ),
        migrations.AddConstraint(
            model_name="deliverypricingprofile",
            constraint=models.CheckConstraint(condition=models.Q(("base_fee__gte", 0)), name="deliverypricing_base_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="deliverypricingprofile",
            constraint=models.CheckConstraint(condition=models.Q(("per_km_fee__gte", 0)), name="deliverypricing_km_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="deliverypricingprofile",
            constraint=models.CheckConstraint(condition=models.Q(("per_seller_fee__gte", 0)), name="deliverypricing_seller_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="deliverypricingprofile",
            constraint=models.CheckConstraint(condition=models.Q(("rural_surcharge__gte", 0)), name="deliverypricing_rural_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="deliverypricingprofile",
            constraint=models.CheckConstraint(condition=models.Q(("minimum_fee__gte", 0)), name="deliverypricing_min_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="deliverypricingprofile",
            constraint=models.CheckConstraint(condition=models.Q(("maximum_fee__gte", 0)) | models.Q(("maximum_fee__isnull", True)), name="deliverypricing_max_gte_0"),
        ),
        migrations.AddConstraint(
            model_name="deliverypricingprofile",
            constraint=models.CheckConstraint(condition=models.Q(("rounding_step__gt", 0)), name="deliverypricing_rounding_gt_0"),
        ),
        migrations.RunPython(seed_eldoret_fulfillment, migrations.RunPython.noop),
    ]
