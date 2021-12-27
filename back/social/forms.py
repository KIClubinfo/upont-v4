from django import forms
from django.core.validators import RegexValidator

from .models import Student


class EditProfile(forms.ModelForm):
    class Meta:
        model = Student
        fields = ("phone_number", "department", "picture")
        widgets = {
            "phone_number": forms.TextInput(attrs={"class": "profil-input"}),
        }

    def __init__(self, *args, **kwargs):
        super(EditProfile, self).__init__(*args, **kwargs)
        self.fields["department"].required = False
        self.fields["phone_number"].required = False
