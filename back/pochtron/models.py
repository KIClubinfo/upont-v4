from django.db import models
from trade.models import Good


class Alcohol(Good):
    degree = models.IntegerField("degree (permil)")
    volume = models.IntegerField("volume (mL)")

    def __str__(self):
        return self.name
