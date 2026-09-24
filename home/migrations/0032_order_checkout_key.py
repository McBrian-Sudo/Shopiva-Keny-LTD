from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0031_order_delivery_proof"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="checkout_key",
            field=models.UUIDField(default=uuid.uuid4, db_index=True, editable=False, unique=True),
        ),
    ]
