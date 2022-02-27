from django import forms

from .models import Price


class EditPrice(forms.ModelForm):
    class Meta:
        model = Price
        fields = ("good", "date", "price")
        widgets = {"price": forms.TextInput(attrs={"class": "profil-input"})}

    def __init__(self, *args, **kwargs):
        super(EditPrice, self).__init__(*args, **kwargs)
