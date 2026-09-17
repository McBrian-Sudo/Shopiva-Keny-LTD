from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="SupportTicket",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("role", models.CharField(choices=[("customer", "Customer"), ("seller", "Seller")], max_length=20)),
                ("subject", models.CharField(max_length=160)),
                ("category", models.CharField(default="General", max_length=80)),
                ("priority", models.CharField(choices=[("normal", "Normal"), ("high", "High"), ("urgent", "Urgent")], default="normal", max_length=20)),
                ("status", models.CharField(choices=[("open", "Open"), ("in_progress", "In progress"), ("waiting_for_customer", "Waiting for customer"), ("resolved", "Resolved"), ("closed", "Closed")], default="open", max_length=30)),
                ("order_reference", models.CharField(blank=True, max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("last_response_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="shopiva_support_tickets", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("-updated_at",),
                "indexes": [
                    models.Index(fields=["user", "status"], name="support_suptick_user_id_8f5f4f_idx"),
                    models.Index(fields=["status", "priority", "updated_at"], name="support_suptick_status_6e0c5a_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="SupportMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("body", models.TextField()),
                ("from_staff", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("author", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="shopiva_support_messages", to=settings.AUTH_USER_MODEL)),
                ("ticket", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="support.supportticket")),
            ],
            options={
                "ordering": ("created_at",),
                "indexes": [models.Index(fields=["ticket", "created_at"], name="support_suptick_ticket__b1bcfe_idx")],
            },
        ),
    ]
