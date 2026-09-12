from django.db import migrations


def ensure_payment_status_column(apps, schema_editor):
    """Ensure the legacy Order.payment_status column exists on every DB backend.

    The old migration used PostgreSQL-specific ALTER TABLE syntax (including
    IF NOT EXISTS and ALTER COLUMN ... DROP DEFAULT), which breaks Django's
    SQLite test database. Keep the historical migration compatible with both
    SQLite and PostgreSQL so fresh CI databases can be created safely.
    """
    connection = schema_editor.connection
    table_name = "home_order"

    with connection.cursor() as cursor:
        description = connection.introspection.get_table_description(cursor, table_name)
        columns = {column.name for column in description}

    if "payment_status" in columns:
        return

    if connection.vendor == "sqlite":
        schema_editor.execute(
            "ALTER TABLE home_order ADD COLUMN payment_status varchar(20) "
            "NOT NULL DEFAULT 'unpaid'"
        )
        return

    # PostgreSQL and other databases that support the original operation.
    schema_editor.execute(
        "ALTER TABLE home_order "
        "ADD COLUMN IF NOT EXISTS payment_status varchar(20) "
        "NOT NULL DEFAULT 'unpaid'"
    )
    if connection.vendor == "postgresql":
        schema_editor.execute(
            "ALTER TABLE home_order "
            "ALTER COLUMN payment_status DROP DEFAULT"
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
