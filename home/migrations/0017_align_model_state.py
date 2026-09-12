from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0016_enforce_platform_commission"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notificationdelivery",
            name="provider_message_id",
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AlterField(
            model_name="notificationdelivery",
            name="provider_status",
            field=models.CharField(blank=True, max_length=120),
        ),
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
