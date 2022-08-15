from django import forms

from .models import Alcohol, PochtronAdmin


class EditAlcohol(forms.ModelForm):
    class Meta:
        model = Alcohol
        fields = (
            "name",
            "club",
            "degree",
            "volume",
        )
        widgets = {
            "name": forms.TextInput(attrs={"class": "profil-input"}),
            "degree": forms.TextInput(attrs={"class": "profil-input"}),
            "volume": forms.TextInput(attrs={"class": "profil-input"}),
        }

    def __init__(self, *args, **kwargs):
        super(EditAlcohol, self).__init__(*args, **kwargs)


class EditPochtronAdmin(forms.ModelForm):
    class Meta:
        model = PochtronAdmin
        fields = (
            "student",
            "alcohol",
            "credit",
            "manage_admins",
        )
