# Generated by Django 3.2.6 on 2021-11-08 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("social", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="club",
            name="category",
        ),
        migrations.AddField(
            model_name="club",
            name="category",
            field=models.ManyToManyField(
                blank=True, related_name="category", to="social.Category"
            ),
        ),
    ]
