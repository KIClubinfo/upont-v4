# Generated by Django 3.2.12 on 2022-10-12 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("social", "0005_merge_0004_auto_20220218_1519_0004_auto_20220811_2021"),
    ]

    operations = [
        migrations.AlterField(
            model_name="role",
            name="name",
            field=models.CharField(max_length=30),
        ),
    ]
