from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0025_auto_20260228_1936"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="reply_to",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="replies",
                to="social.message",
            ),
        ),
        migrations.CreateModel(
            name="MessageReaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("emoji", models.CharField(max_length=32)),
                ("date", models.DateTimeField(auto_now_add=True)),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reactions",
                        to="social.message",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="message_reactions",
                        to="social.student",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("message", "student"), name="unique_message_reaction"
                    )
                ],
            },
        ),
    ]

