from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0037_order_pickup_point"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShopivaBranch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("code", models.CharField(max_length=40, unique=True)),
                ("county", models.CharField(max_length=100)),
                ("town", models.CharField(max_length=120)),
                ("address", models.CharField(max_length=255)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("opening_time", models.TimeField(blank=True, null=True)),
                ("closing_time", models.TimeField(blank=True, null=True)),
                ("services", models.TextField(blank=True, help_text="Customer-facing services offered at this branch.")),
                ("is_headquarters", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("county", "town", "name")},
        ),
        migrations.CreateModel(
            name="ShopivaOutlet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("code", models.CharField(max_length=40, unique=True)),
                ("county", models.CharField(max_length=100)),
                ("town", models.CharField(max_length=120)),
                ("address", models.CharField(max_length=255)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("opening_time", models.TimeField(blank=True, null=True)),
                ("closing_time", models.TimeField(blank=True, null=True)),
                ("services", models.TextField(blank=True, help_text="Customer-facing services offered at this outlet.")),
                ("pickup_available", models.BooleanField(default=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("branch", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="outlets", to="home.shopivabranch")),
            ],
            options={"ordering": ("county", "town", "name")},
        ),
    ]
