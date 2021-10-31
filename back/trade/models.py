from django.db import models


class Good(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField() #in 100th of euros
    club = models.ForeignKey('social.Club', on_delete=models.CASCADE, null=True)


class Transaction(models.Model):
    good = models.ForeignKey('Good', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    student = models.ForeignKey('social.Student', on_delete=models.CASCADE)
    date = models.DateTimeField()