from django.db import models


class Price(models.Model):  # changing prices are handled with a Price model
    good = models.ForeignKey("trade.Good", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField()
    price = models.IntegerField()  # in 100th of euros


class Good(models.Model):
    name = models.CharField(max_length=50)
    club = models.ForeignKey("social.Club", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    def price_object(self):
        return Price.objects.filter(good=self).order_by("-date")[0]

    def price(self):
        return self.price_object().price

    def price_at_date(self, date):
        return (
            Price.objects.filter(good=self, date__lte=date).order_by("-date")[0].price
        )


class Transaction(models.Model):
    good = models.ForeignKey("Good", on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    student = models.ForeignKey("social.Student", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField()

    def __str__(self):
        string_to_return = self.good.name + " : "
        if self.student is not None:
            string_to_return += self.student.user.username
        return string_to_return

    def balance_change_for_student(self):
        return -(self.quantity * self.good.price_at_date(self.date))

    def balance_change_for_club(self):
        return self.quantity * self.good.price_at_date(self.date)
