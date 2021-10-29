from django.contrib import admin

from .models import Transaction, Good

admin.site.register(Transaction)
admin.site.register(Good)