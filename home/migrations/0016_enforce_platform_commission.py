from decimal import Decimal

from django.db import migrations


def normalize_legacy_commissions(apps, schema_editor):
    SellerProfile = apps.get_model("home", "SellerProfile")
    SellerProfile.objects.all().update(commission_percent=Decimal("10.00"))


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0015_align_current_model_indexes"),
    ]

    operations = [
        # Normalize legacy records. The SellerProfile.save() guard below
        # enforces the same 10% platform rate on every future save.
        migrations.RunPython(normalize_legacy_commissions, migrations.RunPython.noop),
    ]
