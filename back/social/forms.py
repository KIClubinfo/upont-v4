from django import forms
from django.core.validators import RegexValidator

from .models import Club, Student


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


class EditClub(forms.ModelForm):
    class Meta:
        model = Club
        fields = ("name", "nickname", "logo", "description")   # , "active", "has_fee", "category", "members"
        #widgets = {
        #    "phone_number": forms.TextInput(attrs={"class": "profil-input"}),
        #}

    def __init__(self, *args, **kwargs):
        super(EditClub, self).__init__(*args, **kwargs)
        self.fields["name"].required = False
        self.fields["nickname"].required = False
        self.fields["logo"].required = False
        self.fields["description"].required = False
        # self.fields["active"].required = False
        # self.fields["has_fee"].required = False
        # self.fields["category"].required = False
        # self.fields["members"].required = False

