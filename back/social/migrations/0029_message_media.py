import social.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0028_message_poll_multi_vote"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="kind",
            field=models.CharField(
                choices=[
                    ("text", "Texte"),
                    ("image", "Image"),
                    ("gif", "GIF"),
                    ("video", "Video"),
                ],
                default="text",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="media_file",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=social.models.message_media_upload_to,
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="media_mime_type",
            field=models.CharField(blank=True, default="", max_length=128),
        ),
        migrations.AddField(
            model_name="message",
            name="media_original_name",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="message",
            name="media_size",
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
    ]
