from django.db import models
from trade.models import Good


class Alcohol(Good):
    degree = models.DecimalField(max_digits=5, decimal_places=2)
    volume = models.DecimalField(max_digits=6, decimal_places=3)
    def __str__(self):
        return self.name
