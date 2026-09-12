from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("home", "0020_google_maps_locations")]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS home_shopivabranding (
                    id BIGSERIAL PRIMARY KEY,
                    app_code VARCHAR(40) NOT NULL UNIQUE,
                    app_name VARCHAR(120) NOT NULL,
                    logo_path VARCHAR(255) NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                INSERT INTO home_shopivabranding
                    (app_code, app_name, logo_path, is_active)
                VALUES
                    ('customer', 'Shopiva Customer Shopping App', 'branding/shopiva-shopping-logo.svg', TRUE)
                ON CONFLICT (app_code) DO UPDATE SET
                    app_name = EXCLUDED.app_name,
                    logo_path = EXCLUDED.logo_path,
                    is_active = TRUE,
                    updated_at = NOW();
            """,
            reverse_sql="DROP TABLE IF EXISTS home_shopivabranding;",
        )
    ]
