from django import forms

from .models import Price, Transaction


class EditPrice(forms.ModelForm):
    class Meta:
        model = Price
        fields = ("good", "date", "price")
        widgets = {"price": forms.TextInput(attrs={"class": "profil-input"})}

    def __init__(self, *args, **kwargs):
        super(EditPrice, self).__init__(*args, **kwargs)


class AddTransaction(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ("good", "quantity", "student", "date")
        widgets = {
            "good": forms.TextInput(attrs={"class": "profil-input"}),
            "quantity": forms.TextInput(attrs={"class": "profil-input"}),
            "student": forms.TextInput(attrs={"class": "profil-input"}),
        }

    def __init__(self, *args, **kwargs):
        super(AddTransaction, self).__init__(*args, **kwargs)
