from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0028_order_delivery_source"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="brand",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="product",
            name="gtin",
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name="product",
            name="mpn",
            field=models.CharField(blank=True, max_length=70),
        ),
    ]
