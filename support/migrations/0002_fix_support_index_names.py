from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("support", "0001_initial"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="supportticket",
            old_name="support_suptick_user_id_8f5f4f_idx",
            new_name="support_ticket_user_stat_idx",
        ),
        migrations.RenameIndex(
            model_name="supportticket",
            old_name="support_suptick_status_6e0c5a_idx",
            new_name="support_ticket_status_pri_idx",
        ),
        migrations.RenameIndex(
            model_name="supportmessage",
            old_name="support_suptick_ticket__b1bcfe_idx",
            new_name="support_msg_ticket_created_idx",
        ),
    ]
