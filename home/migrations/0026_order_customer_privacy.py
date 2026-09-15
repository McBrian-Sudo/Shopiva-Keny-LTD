from django.conf import settings
from django.db import migrations, models
import uuid


def backfill_order_customers(apps, schema_editor):
    Order = apps.get_model("home", "Order")
    User = apps.get_model(*settings.AUTH_USER_MODEL.split(".", 1))
    for order in Order.objects.filter(customer__isnull=True).iterator():
        matches = list(User.objects.filter(email__iexact=order.email, is_active=True).values_list("id", flat=True)[:2])
        if len(matches) == 1:
            Order.objects.filter(pk=order.pk).update(customer_id=matches[0])


class Migration(migrations.Migration):
    dependencies = [("home", "0025_productmedia")]
    operations = [
        migrations.AddField(
            model_name="order",
            name="customer",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=models.deletion.SET_NULL,
                related_name="shopiva_orders", to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="access_token",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.RunPython(backfill_order_customers, migrations.RunPython.noop),
    ]
