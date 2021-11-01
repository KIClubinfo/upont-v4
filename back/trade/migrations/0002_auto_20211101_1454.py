# Generated by Django 3.2.6 on 2021-11-01 14:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("social", "0002_auto_20211101_1454"),
        ("trade", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="good",
            name="club",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="social.club",
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="good",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to="trade.good"
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="student",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="social.student",
            ),
        ),
    ]
