from django.apps import AppConfig
from django.db.models.signals import post_save


class NewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "news"

    def ready(self):
        from . import signals

        post_save.connect(signals.on_post_create, sender="news.Post")
