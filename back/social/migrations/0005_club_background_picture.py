# Generated by Django 3.2.10 on 2022-01-03 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0004_add_pg_trgm'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='background_picture',
            field=models.ImageField(blank=True, null=True, upload_to='club_background_picture'),
        ),
    ]