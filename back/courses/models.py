from io import BytesIO
from uuid import uuid4

from django.contrib.auth import models as models2
from django.core.files import File
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image
from trade.models import Transaction
from unidecode import unidecode

class Ressources(models.Model):
    name=models.CharField(max_length=50, default="Ressource")
    author = models.ForeignKey(
        "social.Student", verbose_name="author", on_delete=models.SET_NULL, null=True
    )
    date = models.DateTimeField()
    file= FileField(
        "Fichier",upload_to='ressources', null=TRUE,blank=TRUE
        )
