from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0027_message_polls"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="messagepollvote",
            name="unique_poll_vote",
        ),
        migrations.AddConstraint(
            model_name="messagepollvote",
            constraint=models.UniqueConstraint(
                fields=("poll", "option", "student"),
                name="unique_poll_option_vote",
            ),
        ),
    ]
