from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0027_merge_pricing_and_privacy"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="delivery_distance_source",
            field=models.CharField(default="estimated", max_length=30),
        ),
    ]
