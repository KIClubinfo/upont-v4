from django.contrib import admin
from .models import Apartment, Room

class ApartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "adress")
    ordering = ("name",)

admin.site.register(Apartment, ApartmentAdmin)
admin.site.register(Room)