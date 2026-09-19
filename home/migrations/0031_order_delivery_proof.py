from django.db import migrations, models
import secrets
import string


def seed_delivery_codes(apps, schema_editor):
    Order = apps.get_model("home", "Order")
    for order in Order.objects.filter(delivery_confirmation_code=""):
        order.delivery_confirmation_code = "".join(secrets.choice(string.digits) for _ in range(6))
        order.save(update_fields=["delivery_confirmation_code"])


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0030_alter_sellerprofile_commission_percent"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="delivery_confirmation_code",
            field=models.CharField(blank=True, editable=False, max_length=6),
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_verification_attempts",
            field=models.PositiveSmallIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_verification_locked_at",
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="delivered_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(seed_delivery_codes, migrations.RunPython.noop),
    ]
