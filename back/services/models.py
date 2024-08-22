from django.db import models
from django.contrib.auth import models as models2


class Bike(models.Model):
    name = models.CharField(max_length=50)
    is_borrowed = models.BooleanField(default=False)
    borrower_id = models.IntegerField(default=-1)

    def __str__(self):
        return self.name.__str__()