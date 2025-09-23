from decimal import Decimal

from django import forms
from django.contrib import admin

from .models import (
    Bike,
    Order,
    OrderItem,
    Vrac,
    RequestForm,
    ReservationMusicRoom,
    Local,
    MedItem,
    Mediatek,
)


class VracAdminForm(forms.ModelForm):
    # Fields for entering comma-separated values
    price_list = forms.CharField(
        help_text="Enter prices separated by commas (e.g.: 10.50,12.75,15.00)",
        required=False,
    )
    stock_list = forms.CharField(
        help_text="Enter stock quantities separated by commas (e.g.: 100,150,200)",
        required=False,
    )
    stock_available_list = forms.CharField(
        help_text="Enter available stock quantities separated by commas (e.g.: 100,150,200)",
        required=False,
    )

    class Meta:
        model = Vrac
        fields = ["name", "type", "price_list", "stock_list", "stock_available_list"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # If editing existing instance
            self.fields["price_list"].initial = ",".join(
                str(p) for p in self.instance.price
            )
            self.fields["stock_list"].initial = ",".join(
                str(s) for s in self.instance.stock
            )
            self.fields["stock_available_list"].initial = ",".join(
                str(s) for s in self.instance.stock_available
            )

    def clean(self):
        cleaned_data = super().clean()
        try:
            # Convert comma-separated strings to lists
            if cleaned_data.get("price_list"):
                cleaned_data["price"] = [
                    Decimal(x.strip()) for x in cleaned_data["price_list"].split(",")
                ]
            if cleaned_data.get("stock_list"):
                cleaned_data["stock"] = [
                    int(x.strip()) for x in cleaned_data["stock_list"].split(",")
                ]
            if cleaned_data.get("stock_available_list"):
                cleaned_data["stock_available"] = [
                    int(x.strip())
                    for x in cleaned_data["stock_available_list"].split(",")
                ]

            # Verify lists have same length
            if len(cleaned_data.get("price", [])) != len(
                cleaned_data.get("stock", [])
            ) or len(cleaned_data.get("stock", [])) != len(
                cleaned_data.get("stock_available", [])
            ):
                raise forms.ValidationError("All lists must have the same length")

        except ValueError:
            raise forms.ValidationError(
                "Please enter valid numbers separated by commas"
            )
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("price"):
            instance.price = self.cleaned_data["price"]
        if self.cleaned_data.get("stock"):
            instance.stock = self.cleaned_data["stock"]
        if self.cleaned_data.get("stock_available"):
            instance.stock_available = self.cleaned_data["stock_available"]

        if commit:
            instance.save()
        return instance


@admin.register(Vrac)
class VracAdmin(admin.ModelAdmin):
    form = VracAdminForm
    list_display = (
        "name",
        "type",
        "display_price",
        "display_stock",
        "display_stock_available",
    )

    def display_price(self, obj):
        return ", ".join(str(p) for p in obj.price)

    display_price.short_description = "Price"

    def display_stock(self, obj):
        return ", ".join(str(s) for s in obj.stock)

    display_stock.short_description = "Stock"

    def display_stock_available(self, obj):
        return ", ".join(str(s) for s in obj.stock_available)

    display_stock_available.short_description = "Stock Available"


@admin.register(RequestForm)
class RequestFormAdmin(admin.ModelAdmin):
    list_display = ("name", "service", "status")
    list_filter = ("service", "status")
    search_fields = ("name", "message")

    actions = ["mark_as_done"]

    def mark_as_done(self, request, queryset):
        queryset.update(status="done")

    mark_as_done.short_description = "Mark selected requests as done"


@admin.register(ReservationMusicRoom)
class ReservationMusicRoomAdmin(admin.ModelAdmin):
    list_display = ("borrower_id", "name", "start_date", "end_date")
    list_filter = ("start_date", "end_date")
    search_fields = ("borrower_id", "name")


@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    list_display = ("name", "get_name_display", "is_open")
    list_filter = ("name", "is_open")
    search_fields = ("name", "description")


@admin.register(MedItem)
class MedItemAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "author", "year", "is_available")
    list_filter = ("type", "is_available", "year")
    search_fields = ("title", "author", "year")


# Register other models
admin.site.register(Bike)
admin.site.register(Order)
admin.site.register(OrderItem)
