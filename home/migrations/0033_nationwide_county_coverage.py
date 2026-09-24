from decimal import Decimal
from django.db import migrations, models


COUNTY_COVERAGE_FEES = (
    ("Baringo", "550.00"),
    ("Bomet", "500.00"),
    ("Bungoma", "500.00"),
    ("Busia", "550.00"),
    ("Elgeyo Marakwet", "550.00"),
    ("Embu", "450.00"),
    ("Garissa", "650.00"),
    ("Homa Bay", "550.00"),
    ("Isiolo", "500.00"),
    ("Kajiado", "400.00"),
    ("Kakamega", "500.00"),
    ("Kericho", "500.00"),
    ("Kiambu", "350.00"),
    ("Kilifi", "600.00"),
    ("Kirinyaga", "400.00"),
    ("Kisii", "550.00"),
    ("Kisumu", "450.00"),
    ("Kitui", "500.00"),
    ("Kwale", "600.00"),
    ("Laikipia", "450.00"),
    ("Lamu", "750.00"),
    ("Machakos", "350.00"),
    ("Makueni", "450.00"),
    ("Mandera", "900.00"),
    ("Marsabit", "750.00"),
    ("Meru", "500.00"),
    ("Migori", "600.00"),
    ("Mombasa", "500.00"),
    ("Murang'a", "350.00"),
    ("Nairobi", "250.00"),
    ("Nakuru", "400.00"),
    ("Nandi", "500.00"),
    ("Narok", "450.00"),
    ("Nyamira", "550.00"),
    ("Nyandarua", "450.00"),
    ("Nyeri", "400.00"),
    ("Samburu", "600.00"),
    ("Siaya", "550.00"),
    ("Taita Taveta", "650.00"),
    ("Tana River", "650.00"),
    ("Tharaka Nithi", "450.00"),
    ("Trans Nzoia", "500.00"),
    ("Turkana", "800.00"),
    ("Uasin Gishu", "450.00"),
    ("Vihiga", "500.00"),
    ("Wajir", "750.00"),
    ("West Pokot", "600.00"),
)


def seed_county_coverage(apps, schema_editor):
    DeliveryTariff = apps.get_model("home", "DeliveryTariff")

    # Correct the legacy seed where Mumias was accidentally stored as a county.
    legacy = DeliveryTariff.objects.filter(county="Mumias", destination="Mumias").first()
    if legacy:
        existing = DeliveryTariff.objects.filter(county="Kakamega", destination="Mumias").first()
        if existing:
            legacy.delete()
        else:
            legacy.county = "Kakamega"
            legacy.save(update_fields=["county"])

    for county, fee in COUNTY_COVERAGE_FEES:
        DeliveryTariff.objects.update_or_create(
            county=county,
            destination="All other destinations",
            defaults={
                "standard_fee": Decimal(fee),
                "pickup_fee": None,
                "express_fee": None,
                "pickup_available": False,
                "express_available": False,
                "is_active": True,
                "is_fallback": True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0032_delivery_tariff"),
    ]

    operations = [
        migrations.AddField(
            model_name="deliverytariff",
            name="is_fallback",
            field=models.BooleanField(
                default=False,
                help_text="Use this tariff for any other delivery point in the county when no exact destination tariff exists.",
            ),
        ),
        migrations.RunPython(seed_county_coverage, migrations.RunPython.noop),
    ]
