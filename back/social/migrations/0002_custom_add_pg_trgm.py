# This migration was not generated automatically. Be careful that you DON'T DELETE IT !
from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0001_initial"),
    ]

    operations = [
        TrigramExtension(),
    ]
