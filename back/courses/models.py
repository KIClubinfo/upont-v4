from django.contrib.auth import models as models2
from django.core.files import File
from django.db import models



class Ressources(models.Model):
    name=models.CharField(max_length=50, default="Ressource")
    author = models.ForeignKey(
        "social.Student", verbose_name="author", on_delete=models.SET_NULL, null=True
    )
    date = models.DateTimeField()
    file= FileField(
        "Fichier",upload_to='ressources', null=TRUE,blank=TRUE
        )
