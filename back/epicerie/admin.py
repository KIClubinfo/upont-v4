from django.contrib import admin

from .models import (
    Basket,
    BasketOrder,
    Vegetable,
    Vrac,
    VracOrder,
    Product,
    ProductOrder,
)

# Register your models here.

admin.site.register(Basket)
admin.site.register(BasketOrder)

admin.site.register(Vrac)
admin.site.register(VracOrder)
admin.site.register(Product)

admin.site.register(Vegetable)

admin.site.register(ProductOrder)
