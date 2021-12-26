from django import forms
from django.core.validators import RegexValidator

from .models import Student


class EditProfile(forms.Form):
    phone_regex = RegexValidator(
        regex=r"^\+?\d{9,16}$",
        message="Le numéro doit être entré au format: '+999999999'. Jusqu'à 16 chiffres sont autorisés.",
    )
    phone_number = forms.CharField(
        max_length=17,
        required=False,
        validators=[phone_regex],
        widget=forms.TextInput(attrs={"class": "profil-input"}),
    )
    department = forms.ChoiceField(choices=Student.Department.choices, required=False)
