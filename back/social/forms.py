from django import forms
from django.core.validators import RegexValidator

from .models import Club, Membership, Role, Student


class EditProfile(forms.ModelForm):
    class Meta:
        model = Student
        fields = ("phone_number", "department", "picture", "gender")
        widgets = {
            "phone_number": forms.TextInput(
                attrs={
                    "class": "profil-input",
                    "placeholder": "Visible par tous les membres",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(EditProfile, self).__init__(*args, **kwargs)
        self.fields["phone_number"].required = False
        self.fields["gender"].choices = [
            ("Homme", "Homme"),
            ("Femme", "Femme"),
            ("Autre", "Autre"),
        ]
        self.fields["phone_number"].placeholder = "False"


class EditClub(forms.ModelForm):
    class Meta:
        model = Club
        fields = (
            "name",
            "nickname",
            "logo",
            "background_picture",
            "description",
            "active",
            "has_fee",
            "category",
        )
        widgets = {
            "name": forms.TextInput(attrs={"class": "profil-input"}),
            "nickname": forms.TextInput(attrs={"class": "profil-input"}),
            "description": forms.Textarea(attrs={"class": "profil-input"}),
            "category": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super(EditClub, self).__init__(*args, **kwargs)
        self.fields["nickname"].required = False
        self.fields["logo"].required = False
        self.fields["background_picture"].required = False
        self.fields["category"].required = False


class AddMember(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ("student", "role", "is_admin")

    def __init__(self, *args, **kwargs):
        super(AddMember, self).__init__(*args, **kwargs)


class AddRole(forms.ModelForm):
    class Meta:
        model = Role
        fields = ("name",)

    def __init__(self, *args, **kwargs):
        super(AddRole, self).__init__(*args, **kwargs)