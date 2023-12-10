# Generated by Django 3.2.12 on 2023-11-24 10:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0007_auto_20231124_0943"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="isPrice",
            field=models.BooleanField(
                choices=[(True, "Yes"), (False, "No")], default=False
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="isShotgun",
            field=models.BooleanField(
                choices=[(True, "Yes"), (False, "No")], default=False
            ),
        ),
    ]