# Generated by Django 3.2.22 on 2025-04-26 10:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("social", "0018_student_first_connection"),
        ("news", "0012_partnership"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="participation",
            unique_together={("participant", "shotgun")},
        ),
    ]
