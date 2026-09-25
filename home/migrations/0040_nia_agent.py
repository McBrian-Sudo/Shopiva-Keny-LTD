from django.conf import settings
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0039_repair_delivery_schema_drift"),
    ]

    operations = [
        migrations.CreateModel(
            name="NiaCallSession",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("role", models.CharField(choices=[("customer", "Customer"), ("seller", "Seller"), ("admin", "Admin")], max_length=20)),
                ("phone_e164", models.CharField(max_length=20)),
                ("status", models.CharField(choices=[("queued", "Queued"), ("ringing", "Ringing"), ("in-progress", "In progress"), ("completed", "Completed"), ("failed", "Failed"), ("canceled", "Canceled"), ("no-answer", "No answer")], default="queued", max_length=20)),
                ("provider", models.CharField(default="twilio", max_length=30)),
                ("provider_sid", models.CharField(blank=True, db_index=True, max_length=100)),
                ("conversation", models.JSONField(blank=True, default=list)),
                ("last_user_text", models.TextField(blank=True)),
                ("last_ai_text", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="nia_calls", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="NiaTask",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("customer", "Customer"), ("seller", "Seller"), ("admin", "Admin")], max_length=20)),
                ("title", models.CharField(max_length=180)),
                ("instruction", models.TextField()),
                ("trigger_kind", models.CharField(choices=[("manual", "Manual"), ("order", "Order"), ("payment", "Payment"), ("delivery", "Delivery"), ("low_stock", "Low stock"), ("schedule", "Scheduled")], default="manual", max_length=20)),
                ("next_run_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("enabled", models.BooleanField(default=True)),
                ("last_run_at", models.DateTimeField(blank=True, null=True)),
                ("last_result", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="nia_tasks", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("next_run_at", "-created_at")},
        ),
    ]
