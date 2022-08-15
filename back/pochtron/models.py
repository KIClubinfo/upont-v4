from django.db import models
from social.models import Student
from trade.models import Good


class Alcohol(Good):
    degree = models.IntegerField("degree (permil)")
    volume = models.IntegerField("volume (mL)")

    def __str__(self):
        return self.name


class PochtronAdmin(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    manage_admins = models.BooleanField(default=False)
    credit = models.BooleanField(default=False)
    alcohol = models.BooleanField(default=False)

    def __str__(self):
        return "PochtronAdmin : {}".format(self.student.user.username)
