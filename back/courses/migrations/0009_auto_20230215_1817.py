# Generated by Django 3.2.12 on 2023-02-15 17:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0008_merge_0003_auto_20230212_2026_0007_auto_20230117_2329"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="course",
            name="teacher",
        ),
        migrations.AddField(
            model_name="course",
            name="teacher",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="courses.teacher",
            ),
            preserve_default=False,
        ),
    ]