# Generated by Django 3.2.22 on 2023-12-20 17:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('epicerie', '0004_vrac_order_total'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vrac_order',
            name='order',
        ),
        migrations.CreateModel(
            name='ProdcutOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='epicerie.product')),
            ],
        ),
        migrations.AddField(
            model_name='vrac_order',
            name='order',
            field=models.ManyToManyField(to='epicerie.ProdcutOrder'),
        ),
    ]
