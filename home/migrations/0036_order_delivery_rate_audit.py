from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("home", "0035_kilimall_style_fulfillment")]

    operations = [
        migrations.AddField(model_name="order", name="delivery_package_class", field=models.CharField(default="small", max_length=20)),
        migrations.AddField(model_name="order", name="delivery_route_class", field=models.CharField(default="national", max_length=20)),
        migrations.AddField(model_name="order", name="delivery_rate_card", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="orders", to="home.deliveryratecard")),
    ]
