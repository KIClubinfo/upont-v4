from django.contrib import admin

from .models import Good, Transaction

admin.site.register(Transaction)
admin.site.register(Good)
