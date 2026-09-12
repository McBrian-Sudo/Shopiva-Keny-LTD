from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0014_notificationdelivery"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="deliverylocationping",
            old_name="home_deliver_agent_i_6fda9b_idx",
            new_name="home_delive_agent_i_fc8bc7_idx",
        ),
        migrations.RenameIndex(
            model_name="paymenttransaction",
            old_name="home_paym_order_i_1a2c7d_idx",
            new_name="home_paymen_order_i_a55c1e_idx",
        ),
    ]
