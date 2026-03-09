from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0029_message_media"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClubLoanItem",
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
                ("name", models.CharField(max_length=120)),
                ("borrowed_on", models.DateField(blank=True, null=True)),
                ("due_on", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "borrower",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="borrowed_club_items",
                        to="social.student",
                    ),
                ),
                (
                    "club",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="loan_items",
                        to="social.club",
                    ),
                ),
            ],
            options={
                "ordering": ["due_on", "name", "id"],
            },
        ),
    ]
