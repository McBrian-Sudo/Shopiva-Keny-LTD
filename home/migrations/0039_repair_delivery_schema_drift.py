from django.db import migrations


ORDER_FIELDS = (
    "delivery_county",
    "delivery_town",
    "delivery_mode",
    "delivery_hub",
    "delivery_pricing_profile",
    "delivery_pricing_basis",
    "delivery_base_fee",
    "delivery_distance_rate",
    "delivery_distance_charge",
    "delivery_package_class",
    "delivery_route_class",
    "delivery_rate_card",
    "delivery_pickup_point",
)

PRODUCT_FIELDS = (
    "package_class",
    "shipping_weight_kg",
    "package_length_cm",
    "package_width_cm",
    "package_height_cm",
    "fulfillment_ready",
)


def repair_schema(apps, schema_editor):
    connection = schema_editor.connection
    existing_tables = set(connection.introspection.table_names())

    def ensure_fields(model_name, field_names):
        model = apps.get_model("home", model_name)
        table = model._meta.db_table
        if table not in existing_tables:
            return
        columns = {
            col.name
            for col in connection.introspection.get_table_description(connection.cursor(), table)
        }
        for name in field_names:
            field = model._meta.get_field(name)
            column = field.column
            if column in columns:
                continue

            # ForeignKey fields require their referenced table to exist.
            remote = getattr(getattr(field, "remote_field", None), "model", None)
            if remote is not None:
                remote_table = remote._meta.db_table
                if remote_table not in existing_tables:
                    continue

            schema_editor.add_field(model, field)
            columns.add(column)

    ensure_fields("Order", ORDER_FIELDS)
    ensure_fields("Product", PRODUCT_FIELDS)


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0038_shopiva_branches_outlets"),
    ]

    operations = [
        migrations.RunPython(repair_schema, migrations.RunPython.noop),
    ]
