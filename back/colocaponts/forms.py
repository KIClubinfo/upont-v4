from django import forms
from django.shortcuts import get_object_or_404
from social.models import Student

from .models import Room, Apartment


class EditColoc(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = (
            "name",
            #"rooms",
            "description",
            "adress",
        )
        widgets = {
            "name": forms.TextInput(attrs={"class": "profil-input"}),
            "description": forms.Textarea(attrs={"class": "text-input mt-2"}),
            "adress": forms.TextInput(attrs={"class": "profil-input"}),
            #"rooms": forms.SelectMultiple(attrs={"class": "profil-select"}),
        }

    def __init__(self, user_id, *args, **kwargs):
        super(EditColoc, self).__init__(*args, **kwargs)
