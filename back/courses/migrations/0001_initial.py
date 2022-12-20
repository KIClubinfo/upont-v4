# Generated by Django 3.2.12 on 2022-12-12 13:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("social", "0007_merge_0004_auto_20220826_1123_0006_alter_role_name"),
        ("news", "0003_auto_20220827_1112"),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
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
                ("name", models.CharField(default="Cours sans nom", max_length=100)),
                ("acronym", models.CharField(default="ABC", max_length=100)),
                (
                    "department",
                    models.CharField(
                        choices=[
                            ("IMI", "Ingénierie mathématique et informatique"),
                            ("GCC", "Génie civil et construction"),
                            ("GMM", "Génie mécanique et matériaux"),
                            ("SEGF", "Sciences économiques, gestion, finance"),
                            ("VET", "Ville, environnement, transport"),
                            ("GI", "Génie industriel"),
                            ("1A", "Première année"),
                            ("DE", "Direction de l'enseignement"),
                            ("DLC", "Département langues et culture"),
                            ("SHS", "Sciences humaines et sociales"),
                            (
                                "PAPDD",
                                "Politique et action publique pour le développement durable",
                            ),
                            ("D.SCHOOL", "d.school"),
                            ("AHE", "Autres hors école"),
                        ],
                        default="AHE",
                        max_length=8,
                    ),
                ),
                ("description", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="Enrolment",
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
                ("is_old", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Teacher",
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
                (
                    "name",
                    models.CharField(default="Professeur anonyme", max_length=100),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Update",
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
                (
                    "new_course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="new",
                        to="courses.course",
                    ),
                ),
                (
                    "old_course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="old",
                        to="courses.course",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Group",
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
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="courses.course"
                    ),
                ),
                (
                    "students",
                    models.ManyToManyField(
                        blank=True,
                        related_name="course",
                        through="courses.Enrolment",
                        to="social.Student",
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="courses.teacher",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="enrolment",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="courses.group"
            ),
        ),
        migrations.AddField(
            model_name="enrolment",
            name="student",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="social.student"
            ),
        ),
        migrations.AddField(
            model_name="course",
            name="head",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="courses.teacher"
            ),
        ),
        migrations.AddField(
            model_name="course",
            name="old_courses",
            field=models.ManyToManyField(
                blank=True,
                related_name="new_courses",
                through="courses.Update",
                to="courses.Course",
            ),
        ),
        migrations.AddField(
            model_name="course",
            name="posts",
            field=models.ManyToManyField(
                blank=True, related_name="course", to="news.Post"
            ),
        ),
    ]