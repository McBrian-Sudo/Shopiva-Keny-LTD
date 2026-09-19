from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0017_align_model_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="items_subtotal",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name="order",
            name="platform_commission_amount",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_fee",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_distance_km",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
