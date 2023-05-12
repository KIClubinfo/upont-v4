from django import forms, extras

from .models import Club, ClubRequest, Membership, Role, Student


class EditProfile(forms.ModelForm):
    class Meta:
        model = Student
        fields = ("phone_number", "department", "picture", "gender", "birthdate", "biography")
        widgets = {
            "phone_number": forms.TextInput(
                attrs={
                    "class": "profil-input",
                    "placeholder": "Numéro de téléphone",
                }
            ),
            "department": forms.Select(attrs={"class": "profil-select"}),
            "picture": forms.FileInput(attrs={"class": "profil-input"}),
            "gender": forms.Select(attrs={"class": "profil-select"}),
            "birthdate": forms.DateField(widget=extras.SelectDateWidget, format = '%d/%m/%Y'),
            "biography": forms.Textarea(attrs={"class": "profil-input"})
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
        self.fields["birthdate"].required = False
        self.fields["biography"].required = False



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
            "logo": forms.FileInput(attrs={"class": "profil-input"}),
            "background_picture": forms.FileInput(attrs={"class": "profil-input"}),
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
        widgets = {
            "student": forms.Select(attrs={"class": "profil-select"}),
            "role": forms.Select(attrs={"class": "profil-select"}),
        }

    def __init__(self, *args, **kwargs):
        super(AddMember, self).__init__(*args, **kwargs)


class AddRole(forms.ModelForm):
    class Meta:
        model = Role
        fields = ("name",)
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "profil-input profil-member-create"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(AddRole, self).__init__(*args, **kwargs)


class ClubRequestForm(forms.ModelForm):
    class Meta:
        model = ClubRequest
        fields = (
            "name",
            "content",
        )
        widgets = {
            "name": forms.TextInput(attrs={"class": "profil-input"}),
            "content": forms.Textarea(attrs={"class": "text-input"}),
        }
