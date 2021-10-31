from django.contrib import admin

from .models import Good, Transaction

admin.site.register(Good)
admin.site.register(Transaction)