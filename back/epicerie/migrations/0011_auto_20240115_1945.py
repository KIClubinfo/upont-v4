# Generated by Django 3.2.22 on 2024-01-15 18:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("epicerie", "0010_auto_20240109_1833"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="vrac",
            name="ListProducts",
        ),
        migrations.AddField(
            model_name="product",
            name="vrac",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="epicerie.vrac",
            ),
        ),
    ]
