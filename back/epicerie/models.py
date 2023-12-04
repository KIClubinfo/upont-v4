from django.db import models

# Create your models here.


class Vegetable(models.Model):
    name = models.CharField(max_length=50)  # Name of the vegetable
    quantity = models.IntegerField(default=0)  # Quantity (in grams)
    
    def __str__(self):
        return f"{self.name} ({self.quantity}g)"
    

class Basket(models.Model):
    price = models.IntegerField(default=0)  # in cents
    composition = models.ManyToManyField(Vegetable)
    open_date = models.DateTimeField()
    close_date = models.DateTimeField()
    pickup_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        date = f"{self.pickup_date.day}/{self.pickup_date.month}"
        return f"panier à {self.price/100}€ du {date}"
    
    def displayPrice(self):
        return f"{self.price/100}€"
    
    def listComposition(self):
        return [str(v) for v in self.composition.all()]


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
