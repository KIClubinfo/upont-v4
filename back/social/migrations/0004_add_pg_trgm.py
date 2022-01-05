from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0003_alter_club_nickname"),
    ]

    operations = [
        TrigramExtension(),
    ]
