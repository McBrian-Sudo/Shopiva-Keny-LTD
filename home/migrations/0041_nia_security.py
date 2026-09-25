from django.conf import settings
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0040_nia_agent"),
    ]

    operations = [
        migrations.CreateModel(
            name="NiaCallerVerification",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("role", models.CharField(choices=[("customer", "Customer"), ("seller", "Seller"), ("admin", "Admin")], max_length=20)),
                ("phone_e164", models.CharField(db_index=True, max_length=20)),
                ("pin_code", models.CharField(max_length=4)),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("expires_at", models.DateTimeField(db_index=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="nia_caller_verifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("-created_at",),
                "indexes": [
                    models.Index(fields=("phone_e164", "expires_at"), name="home_niacall_phone_2e0c3b_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="NiaAuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("customer", "Customer"), ("seller", "Seller"), ("admin", "Admin")], max_length=20)),
                ("action", models.CharField(max_length=100)),
                ("detail", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="nia_audit_logs", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("-created_at",),
                "indexes": [
                    models.Index(fields=("user", "created_at"), name="home_niaaudit_user_63c0df_idx"),
                    models.Index(fields=("role", "action", "created_at"), name="home_niaaudit_role_91b8cc_idx"),
                ],
            },
        ),
        migrations.AddField(
            model_name="niacallsession",
            name="direction",
            field=models.CharField(choices=[("outbound", "Outbound"), ("inbound", "Inbound")], default="outbound", max_length=10),
        ),
        migrations.AddField(
            model_name="niacallsession",
            name="caller_verified",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="niacallsession",
            name="verification",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="call_sessions", to="home.niacallerverification"),
        ),
    ]
