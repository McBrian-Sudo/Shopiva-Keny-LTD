from django.db import migrations


def cleanup_legacy_constraints(apps, schema_editor):
    """Remove duplicate constraints left by the legacy PostgreSQL repair migration.

    These constraints duplicate Django's canonical foreign keys. Dropping only the
    redundant constraints does not alter application data or the effective FK
    behavior, because the canonical Django constraints remain in place.
    """
    if schema_editor.connection.vendor != "postgresql":
        return

    statements = [
        "ALTER TABLE home_product DROP CONSTRAINT IF EXISTS home_product_seller_id_fk_repair",
        "ALTER TABLE home_orderitem DROP CONSTRAINT IF EXISTS home_orderitem_seller_id_fk_repair",
    ]
    with schema_editor.connection.cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0023_update_app_brand_assets"),
    ]

    operations = [
        migrations.RunPython(
            cleanup_legacy_constraints,
            migrations.RunPython.noop,
        ),
    ]
