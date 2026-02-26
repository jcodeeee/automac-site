from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cars", "0004_car_sold_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="car",
            name="body_type",
            field=models.CharField(
                choices=[("Sedan", "Sedan"), ("SUV", "SUV"), ("Van", "Van")],
                default="Sedan",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="car",
            name="seating_capacity",
            field=models.PositiveSmallIntegerField(default=5),
        ),
    ]
