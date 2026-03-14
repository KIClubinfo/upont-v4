from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0030_clubloanitem"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClubLoanCategory",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=80)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "club",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="loan_categories",
                        to="social.club",
                    ),
                ),
            ],
            options={
                "ordering": ["name", "id"],
            },
        ),
        migrations.AddConstraint(
            model_name="clubloancategory",
            constraint=models.UniqueConstraint(
                fields=("club", "name"), name="unique_club_loan_category_name"
            ),
        ),
        migrations.AddField(
            model_name="clubloanitem",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="loan_items",
                to="social.clubloancategory",
            ),
        ),
    ]
