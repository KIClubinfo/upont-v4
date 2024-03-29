# Generated by Django 3.2.11 on 2022-01-19 12:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("trade", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Alcohol",
            fields=[
                (
                    "good_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="trade.good",
                    ),
                ),
                ("degree", models.IntegerField(verbose_name="degree (permil)")),
                ("volume", models.IntegerField(verbose_name="volume (mL)")),
            ],
            bases=("trade.good",),
        ),
    ]
