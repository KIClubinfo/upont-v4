# Generated by Django 3.2.6 on 2021-12-10 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0003_auto_20211209_1518"),
    ]

    operations = [
        migrations.AddField(
            model_name="participation",
            name="motivation",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="shotgun",
            name="ending_date",
            field=models.DateTimeField(),
        ),
    ]