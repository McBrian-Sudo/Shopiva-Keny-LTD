from django.db import migrations


def ensure_payment_status_column(apps, schema_editor):
    schema_editor.execute(
        '''
        ALTER TABLE home_order
        ADD COLUMN IF NOT EXISTS payment_status varchar(20) NOT NULL DEFAULT 'unpaid'
        '''
    )
    schema_editor.execute(
        '''
        ALTER TABLE home_order
        ALTER COLUMN payment_status DROP DEFAULT
        '''
    )


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0008_paymenttransaction"),
    ]

    operations = [
        migrations.RunPython(
            ensure_payment_status_column,
            migrations.RunPython.noop,
        ),
    ]
