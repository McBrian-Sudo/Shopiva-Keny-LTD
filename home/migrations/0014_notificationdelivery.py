from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0013_cloudinary_reviews_notifications"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationDelivery",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("channel", models.CharField(choices=[("email", "Email"), ("sms", "SMS"), ("whatsapp", "WhatsApp")], max_length=20)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("accepted", "Accepted by provider"), ("delivered", "Delivered"), ("failed", "Failed"), ("skipped", "Skipped")], default="pending", max_length=20)),
                ("provider_message_id", models.CharField(blank=True, max_length=255)),
                ("provider_status", models.CharField(blank=True, max_length=100)),
                ("error_message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("delivered_at", models.DateTimeField(blank=True, null=True)),
                ("notification", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="deliveries", to="home.notification")),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.AddConstraint(
            model_name="notificationdelivery",
            constraint=models.UniqueConstraint(fields=("notification", "channel"), name="unique_notification_delivery_channel"),
        ),
    ]
