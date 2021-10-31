# Generated by Django 3.2.6 on 2021-10-31 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='membership',
            name='club',
        ),
        migrations.AddField(
            model_name='membership',
            name='club',
            field=models.ManyToManyField(to='social.Club'),
        ),
        migrations.RemoveField(
            model_name='membership',
            name='student',
        ),
        migrations.AddField(
            model_name='membership',
            name='student',
            field=models.ManyToManyField(to='social.Student'),
        ),
    ]
