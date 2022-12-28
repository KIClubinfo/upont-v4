from django.db import models


class Resources(models.Model):
    name = models.CharField(max_length=50, default="Ressource")
    author = models.ForeignKey(
        "social.Student", verbose_name="author", on_delete=models.SET_NULL, null=True
    )
    date = models.DateTimeField()
    file = models.FileField("Fichier", upload_to="ressources", null=True, blank=True)
    post = models.ForeignKey(
        "news.Post", verbose_name="post", on_delete=models.SET_NULL, null=True
    )
