# Generated by Django 3.2.12 on 2023-07-31 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0008_notificationtoken'),
        ('news', '0006_auto_20230731_1810'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='Page',
            new_name='page',
        ),
        migrations.AddField(
            model_name='page',
            name='members',
            field=models.ManyToManyField(through='news.PageMembership', to='social.Student'),
        ),
    ]