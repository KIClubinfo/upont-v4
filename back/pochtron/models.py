from django.db import models
from trade.models import Good


class Alcohol(Good):
    degree = models.FloatField()
    volume = models.FloatField()
    def __str__(self):
        return self.name
