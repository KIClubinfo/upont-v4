# Generated by Django 3.2.22 on 2023-12-09 21:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0015_alter_student_biography"),
    ]

    operations = [
        migrations.AlterField(
            model_name="club",
            name="nickname",
            field=models.CharField(blank=True, default="", max_length=50, null=True),
        ),
    ]