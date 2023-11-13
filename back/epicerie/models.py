from django.db import models

# Create your models here.

class Basket(models.Model):
    price = models.IntegerField(default=0)          # in cents
    composition = models.TextField()
    open_date = models.DateTimeField()
    close_date = models.DateTimeField()
    pickup_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Panier à {self.price/100}€ du {self.pickup_date}" 

class Basket_Order(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey('social.Student', on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.basker = kwargs.get('basket', None)
        self.student = kwargs.get('student', None)
        self.quantity = kwargs.get('quantity', None)

    def __str__(self):
        return str(self.basket) + " " + str(self.student)
