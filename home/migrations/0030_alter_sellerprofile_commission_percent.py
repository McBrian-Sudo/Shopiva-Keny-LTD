from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0029_product_merchant_identifiers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sellerprofile",
            name="commission_percent",
            field=models.DecimalField(
                decimal_places=2,
                default=10,
                help_text="Shopiva platform commission. Sellers cannot set or change this rate.",
                max_digits=5,
            ),
        ),
    ]
