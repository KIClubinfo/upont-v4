from django.contrib import admin
from .models import Basket, Basket_Order, Vegetable

# Register your models here.

admin.site.register(Basket)
admin.site.register(Basket_Order)
admin.site.register(Vegetable)
