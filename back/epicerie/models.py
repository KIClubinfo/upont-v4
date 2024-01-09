from django.db import models

# Create your models here.


class Basket(models.Model):
    price = models.IntegerField(default=0)  # in cents
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
        return [str(v) for v in Vegetable.objects.filter(basket=self)]
    
class Vegetable(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)  # Name of the vegetable
    quantity = models.IntegerField(default=0)  # Quantity (in grams)

    def __str__(self):
        return f"{self.name} ({self.quantity}g)"


class BasketOrder(models.Model):
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


class Product(models.Model):
    name = models.CharField(max_length=100)
    # step in grams
    step = models.IntegerField(default=50)
    # max quantity in grams
    max = models.IntegerField(default=5000)
    # in cents for 1000 grams
    price = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} à ({self.price/100}€ pour 1kg)"


class Vrac(models.Model):
    # list of products
    ListProducts = models.ManyToManyField(Product)
    # open date for sale
    open_date = models.DateTimeField()
    # close date for sale
    close_date = models.DateTimeField()
    # pickup date for the order
    pickup_date = models.DateTimeField()
    # is the vrac active
    is_active = models.BooleanField(default=True)

    def __str__(self):
        date = f"{self.pickup_date.day}/{self.pickup_date.month}"
        produits = ""
        for product in self.ListProducts.all():
            produits += f"{product.name}, "
        return (
            f"vrac du {date} avec les {self.ListProducts.count()} produits {produits}"
        )

    def getproduct(self):
        # return a list of product
        return [product for product in self.ListProducts]
    
class ProductOrder(models.Model):
    #Each order of one product is linked to a vrac order
    vracOrder = models.ForeignKey("VracOrder", on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)

    def isValid(self):
        bool = self.product is not None
        bool = bool and self.quantity >= 0 and isinstance(self.quantity, int)
        return bool

    def __str__(self) -> str:
        string : str = f"{self.quantity} of {self.product.name}"
        return string

class VracOrder(models.Model):
    vrac = models.ForeignKey(Vrac, on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey("social.Student", on_delete=models.SET_NULL, null=True)
    # order is a dictionnairy taking as key the product name and as value quantity
    total = models.IntegerField(default = 0)

    class Meta:
        unique_together = ("vrac", "student")

    def __str__(self):
        return f"Vrac du {self.vrac.pickup_date} by {self.student}, pour un total de {self.total}"

    def isValid(self):
        quant_pos = all(prodOrder.isValid() for prodOrder in self.order.all())
        return quant_pos
