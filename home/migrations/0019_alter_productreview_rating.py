from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0018_system_integrity_constraints"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productreview",
            name="rating",
            field=models.PositiveSmallIntegerField(
                validators=[MinValueValidator(1), MaxValueValidator(5)]
            ),
        ),
    ]
