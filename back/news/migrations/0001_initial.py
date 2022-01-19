# Generated by Django 3.2.6 on 2022-01-18 20:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("social", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
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
                ("name", models.CharField(max_length=50)),
                ("description", models.TextField()),
                ("date", models.DateTimeField()),
                ("location", models.CharField(max_length=50)),
                (
                    "poster",
                    models.ImageField(blank=True, null=True, upload_to="poster"),
                ),
                (
                    "club",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="social.club",
                    ),
                ),
                (
                    "participants",
                    models.ManyToManyField(
                        blank=True, related_name="events", to="social.Student"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Shotgun",
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
                ("title", models.CharField(max_length=50)),
                ("content", models.TextField()),
                ("date", models.DateTimeField()),
                ("size", models.IntegerField(default=0)),
                ("requires_motivation", models.BooleanField(default=False)),
                (
                    "club",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="social.club",
                        verbose_name="organizing club",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Post",
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
                ("title", models.CharField(max_length=50)),
                ("date", models.DateTimeField()),
                (
                    "illustration",
                    models.ImageField(
                        blank=True, null=True, upload_to="post_illustrations"
                    ),
                ),
                ("content", models.TextField()),
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
                    "club",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="social.club",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="news.event",
                    ),
                ),
                (
                    "likes",
                    models.ManyToManyField(
                        blank=True, related_name="posts", to="social.Student"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Comment",
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
                ("date", models.DateTimeField()),
                ("content", models.TextField()),
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
                    "club",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="social.club",
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="news.post",
                    ),
                ),
            ],
        ),
    ]
