from django.db import migrations


def update_brand_assets(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE home_shopivabranding
            SET logo_path = CASE app_code
                WHEN 'customer' THEN 'shopiva/shopiva-shopping-logo.svg'
                WHEN 'admin' THEN 'shopiva/shopiva-admin-logo.svg'
                ELSE logo_path
            END,
            updated_at = NOW()
            WHERE app_code IN ('customer', 'admin')
            """
        )


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0022_repair_legacy_marketplace_schema"),
    ]

    operations = [
        migrations.RunPython(update_brand_assets, migrations.RunPython.noop),
    ]
