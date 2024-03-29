import upont.notifications as notifications
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Post


@receiver(post_save, sender=Post)
def on_post_create(sender, instance, created, **kwargs):
    if created:
        if instance.club is not None:
            notifications.send_push_message_to_all_students(
                instance.club.name, instance.title
            )
        else:
            notifications.send_push_message_to_all_students(
                instance.author.user.first_name + " " + instance.author.user.last_name,
                instance.title,
            )
