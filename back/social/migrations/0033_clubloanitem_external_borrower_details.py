from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("social", "0032_clubloanitem_borrower_external_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="clubloanitem",
            name="borrower_external_first_name",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
        migrations.AddField(
            model_name="clubloanitem",
            name="borrower_external_last_name",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
        migrations.AddField(
            model_name="clubloanitem",
            name="borrower_external_phone_number",
            field=models.CharField(blank=True, default="", max_length=17),
        ),
    ]
