# Generated by Django 3.2.12 on 2023-11-24 08:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0014_alter_club_label"),
    ]

    operations = [
        migrations.AlterField(
            model_name="student",
            name="biography",
            field=models.TextField(blank=True, max_length=300, null=True),
        ),
    ]
