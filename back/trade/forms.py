from django import forms

from .models import Good, Price, TradeAdmin, Transaction


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


class EditGood(forms.ModelForm):
    class Meta:
        model = Good
        fields = (
            "name",
            "club",
        )

    def __init__(self, *args, **kwargs):
        super(EditGood, self).__init__(*args, **kwargs)


class EditTradeAdmin(forms.ModelForm):
    class Meta:
        model = TradeAdmin
        fields = (
            "student",
            "club",
            "manage_goods",
            "manage_transactions",
            "manage_credits",
            "manage_admins",
        )
