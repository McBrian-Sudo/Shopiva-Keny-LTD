from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("home", "0036_order_delivery_rate_audit")]

    operations = [
        migrations.AddField(
            model_name="order",
            name="delivery_pickup_point",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="orders", to="home.deliverypickuppoint"),
        ),
    ]
