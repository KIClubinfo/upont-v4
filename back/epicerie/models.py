from django.db import models

# Create your models here.


class Basket(models.Model):
    price = models.IntegerField(default=0)  # in cents
    composition = models.TextField()
    open_date = models.DateTimeField()
    close_date = models.DateTimeField()
    pickup_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        date = f"{self.pickup_date.day}/{self.pickup_date.month}"
        return f"panier à {self.price/100}€ du {date}"


class Basket_Order(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey("social.Student", on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.quantity} {self.basket} by {self.student}"

    def isValid(self):
        bool = self.basket is not None
        bool = bool and self.student is not None
        bool = bool and self.quantity >= 0 and isinstance(self.quantity, int)
        return bool
