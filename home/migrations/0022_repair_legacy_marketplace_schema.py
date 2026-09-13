from django.db import migrations


def repair_marketplace_schema(apps, schema_editor):
    """Repair legacy PostgreSQL schemas that were marked migrated but missed columns.

    This is additive and idempotent. It does not delete or rewrite customer,
    order, product, seller, or payment data.
    """
    if schema_editor.connection.vendor != "postgresql":
        return

    statements = [
        """
        ALTER TABLE home_product
        ADD COLUMN IF NOT EXISTS seller_id bigint NULL
        """,
        """
        ALTER TABLE home_orderitem
        ADD COLUMN IF NOT EXISTS seller_id bigint NULL
        """,
        """
        ALTER TABLE home_orderitem
        ADD COLUMN IF NOT EXISTS seller_gross numeric(12,2) NOT NULL DEFAULT 0
        """,
        """
        ALTER TABLE home_orderitem
        ADD COLUMN IF NOT EXISTS platform_commission numeric(12,2) NOT NULL DEFAULT 0
        """,
        """
        ALTER TABLE home_orderitem
        ADD COLUMN IF NOT EXISTS seller_net numeric(12,2) NOT NULL DEFAULT 0
        """,
        """
        ALTER TABLE home_order
        ADD COLUMN IF NOT EXISTS payment_status varchar(20) NOT NULL DEFAULT 'unpaid'
        """,
        """
        ALTER TABLE home_order
        ADD COLUMN IF NOT EXISTS payment_reference varchar(120) NOT NULL DEFAULT ''
        """,
    ]

    with schema_editor.connection.cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)

        cursor.execute(
            """
            DO $$
            BEGIN
                IF to_regclass('home_sellerprofile') IS NOT NULL
                   AND NOT EXISTS (
                       SELECT 1 FROM pg_constraint
                       WHERE conname = 'home_product_seller_id_fk_repair'
                   )
                THEN
                    ALTER TABLE home_product
                    ADD CONSTRAINT home_product_seller_id_fk_repair
                    FOREIGN KEY (seller_id)
                    REFERENCES home_sellerprofile(id)
                    DEFERRABLE INITIALLY DEFERRED;
                END IF;
            END
            $$;
            """
        )

        cursor.execute(
            """
            DO $$
            BEGIN
                IF to_regclass('home_sellerprofile') IS NOT NULL
                   AND NOT EXISTS (
                       SELECT 1 FROM pg_constraint
                       WHERE conname = 'home_orderitem_seller_id_fk_repair'
                   )
                THEN
                    ALTER TABLE home_orderitem
                    ADD CONSTRAINT home_orderitem_seller_id_fk_repair
                    FOREIGN KEY (seller_id)
                    REFERENCES home_sellerprofile(id)
                    DEFERRABLE INITIALLY DEFERRED;
                END IF;
            END
            $$;
            """
        )


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0021_shopiva_branding"),
    ]

    operations = [
        migrations.RunPython(
            repair_marketplace_schema,
            migrations.RunPython.noop,
        ),
    ]
