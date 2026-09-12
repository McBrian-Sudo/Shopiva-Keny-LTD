from decimal import Decimal

from django.db import migrations, models


def normalize_legacy_commissions(apps, schema_editor):
    SellerProfile = apps.get_model("home", "SellerProfile")
    SellerProfile.objects.all().update(commission_percent=Decimal("10.00"))


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0015_align_current_model_indexes"),
    ]

    operations = [
        migrations.RunPython(normalize_legacy_commissions, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="sellerprofile",
            name="commission_percent",
            field=models.DecimalField(
                decimal_places=2,
                default=10,
                editable=False,
                help_text="Managed by Shopiva platform policy; sellers cannot change this.",
                max_digits=5,
            ),
        ),
    ]
