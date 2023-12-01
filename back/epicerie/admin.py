from django.contrib import admin
from .models import Basket, Basket_Order, Vrac, Vrac_Order, Product

# Register your models here.

admin.site.register(Basket)
admin.site.register(Basket_Order)
admin.site.register(Vrac)
admin.site.register(Vrac_Order)
admin.site.register(Product)