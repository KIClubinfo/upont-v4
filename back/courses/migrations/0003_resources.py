# Generated by Django 3.2.12 on 2023-01-02 13:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0007_merge_0004_auto_20220826_1123_0006_alter_role_name"),
        ("news", "0003_auto_20220827_1112"),
        ("courses", "0002_auto_20221212_1511"),
    ]

    operations = [
        migrations.CreateModel(
            name="Resources",
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
                ("name", models.CharField(default="Ressource", max_length=50)),
                ("date", models.DateTimeField()),
                (
                    "file",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="ressources",
                        verbose_name="Fichier",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="social.student",
                        verbose_name="author",
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="news.post",
                        verbose_name="post",
                    ),
                ),
            ],
        ),
    ]
