from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("social", "0031_clubloancategory_and_item_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="clubloanitem",
            name="borrower_external_name",
            field=models.CharField(blank=True, default="", max_length=160),
        ),
    ]
