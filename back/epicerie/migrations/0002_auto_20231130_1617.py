# Generated by Django 3.2.22 on 2023-11-30 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epicerie', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vegetable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('quantity', models.IntegerField(default=0)),
            ],
        ),
        migrations.RemoveField(
            model_name='basket',
            name='composition',
        ),
        migrations.AddField(
            model_name='basket',
            name='composition',
            field=models.ManyToManyField(to='epicerie.Vegetable'),
        ),
    ]
