from django.db import migrations


def create_branding_table(apps, schema_editor):
    """Create the branding table using SQL valid on SQLite and PostgreSQL."""
    vendor = schema_editor.connection.vendor
    with schema_editor.connection.cursor() as cursor:
        if vendor == "postgresql":
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS home_shopivabranding (
                    id BIGSERIAL PRIMARY KEY,
                    app_code VARCHAR(40) NOT NULL UNIQUE,
                    app_name VARCHAR(120) NOT NULL,
                    logo_path VARCHAR(255) NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS home_shopivabranding (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_code VARCHAR(40) NOT NULL UNIQUE,
                    app_name VARCHAR(120) NOT NULL,
                    logo_path VARCHAR(255) NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

        cursor.execute(
            """
            UPDATE home_shopivabranding
            SET app_name = %s,
                logo_path = %s,
                is_active = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE app_code = %s
            """,
            [
                "Shopiva Customer Shopping App",
                "branding/shopiva-shopping-logo.svg",
                True,
                "customer",
            ],
        )
        if cursor.rowcount == 0:
            cursor.execute(
                """
                INSERT INTO home_shopivabranding
                    (app_code, app_name, logo_path, is_active)
                VALUES (%s, %s, %s, %s)
                """,
                [
                    "customer",
                    "Shopiva Customer Shopping App",
                    "branding/shopiva-shopping-logo.svg",
                    True,
                ],
            )


class Migration(migrations.Migration):
    dependencies = [("home", "0020_google_maps_locations")]

    operations = [
        migrations.RunPython(
            create_branding_table,
            migrations.RunPython.noop,
        )
    ]
