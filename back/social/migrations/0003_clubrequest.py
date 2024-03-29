# Generated by Django 3.2.11 on 2022-02-01 11:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0002_custom_add_pg_trgm"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClubRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=30)),
                ("content", models.TextField()),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="social.student"
                    ),
                ),
            ],
        ),
    ]
