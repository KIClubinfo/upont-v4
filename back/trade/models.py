from django.db import models


class Good(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField() #in 100th of euros
    club = models.ForeignKey('social.Club', on_delete=models.CASCADE)
    def __str__(self):
        return self.name


class Transaction(models.Model):
    good = models.ForeignKey('Good', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    student = models.ForeignKey('social.Student', on_delete=models.CASCADE)
    date = models.DateTimeField()
    def __str__(self):
        return self.good.name + ' : ' + self.student.user.username 