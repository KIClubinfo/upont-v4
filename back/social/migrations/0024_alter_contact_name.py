# Generated by Django 3.2.22 on 2024-02-12 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0023_auto_20240212_1535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
