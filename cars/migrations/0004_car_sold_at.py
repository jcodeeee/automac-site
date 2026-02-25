from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cars", "0003_car_main_image_alter_car_owner_booking"),
    ]

    operations = [
        migrations.AddField(
            model_name="car",
            name="sold_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
