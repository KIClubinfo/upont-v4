from django import forms
from django.shortcuts import get_object_or_404

from social.models import Membership, Student

from .models import Comment, Event, Post, Shotgun  # , Sondage


class EditEvent(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            "name",
            "description",
            "date",
            "end",
            "location",
            "poster",
            "club",
            "shotgun",
            "isShotgun",
            "isPrice",
            "organizer",
        )
        widgets = {
            "name": forms.TextInput(attrs={"class": "profil-input"}),
            "description": forms.Textarea(attrs={"class": "text-input mt-2"}),
            "date": forms.TextInput(attrs={"class": "profil-input"}),
            "end": forms.TextInput(attrs={"class": "profil-input"}),
            "location": forms.TextInput(attrs={"class": "profil-input"}),
            "poster": forms.FileInput(attrs={"class": "profil-input"}),
            "club": forms.Select(attrs={"class": "profil-select"}),
            "shotgun": forms.Select(attrs={"class": "profil-select"}),
            "isShotgun": forms.RadioSelect(
                attrs={"class": "profil-select"},
                choices=[(True, "Oui"), (False, "Non")],
            ),
            "isPrice": forms.RadioSelect(
                attrs={"class": "profil-select"},
                choices=[(True, "Oui"), (False, "Non")],
            ),
            "organizer": forms.Select(attrs={"class": "profil-select"}),
        }

    def __init__(self, user_id, *args, **kwargs):
        super(EditEvent, self).__init__(*args, **kwargs)
        self.fields["club"].choices = [
            (membership.club.id, membership.club)
            for membership in Membership.objects.filter(student__user__pk=user_id)
        ]
        shotguns_choices_list = [("", "Pas de shotgun")]
        student = get_object_or_404(Student, user__id=user_id)
        for shotgun in Shotgun.objects.all():
            if shotgun.club.is_member(student.id):
                shotguns_choices_list.append((shotgun.id, shotgun.title))
        self.fields["shotgun"].choices = shotguns_choices_list

    def clean(self):
        cleaned_data = super(EditEvent, self).clean()
        date = cleaned_data.get("date")
        end = cleaned_data.get("end")

        if date and end:  # check if the inputs are valid
            if end <= date:
                self.add_error(
                    "end",
                    "La date de fin doit être postérieure à la date de début",
                )

        return cleaned_data


class EditPost(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "title",
            "illustration",
            "content",
            "event",
            "club",
        )
        widgets = {
            "title": forms.TextInput(attrs={"class": "profil-input"}),
            "illustration": forms.FileInput(attrs={"class": "profil-input"}),
            "content": forms.Textarea(attrs={"class": "text-input mt-2"}),
            "event": forms.Select(attrs={"class": "profil-select"}),
            "club": forms.Select(attrs={"class": "profil-select"}),
            "video": forms.TextInput(attrs={"class": "profil-input"}),
        }

    def __init__(self, user_id, *args, **kwargs):
        super(EditPost, self).__init__(*args, **kwargs)
        self.fields["event"].choices = [("", "Aucun")] + [
            (event.id, event)
            for event in Event.objects.filter(
                club__in=Membership.objects.filter(student__user__pk=user_id).values(
                    "club"
                )
            )
        ]
        self.fields["club"].choices = [("", "Élève")] + [
            (membership.club.id, membership.club)
            for membership in Membership.objects.filter(student__user__pk=user_id)
        ]
        self.fields["resource_file"] = forms.FileField(
            widget=forms.FileInput(
                attrs={
                    "class": "profil-input"}),
            required=False)
        self.fields["video"] = forms.URLField(
            widget=forms.TextInput(
                attrs={
                    "class": "profil-input"}),
            required=False)


""" class EditSondage(forms.ModelForm):
    class Meta:
        model = Sondage
        fields = (
            "title",
            "content",
            "club",
        )
        widgets = {
            "title": forms.TextInput(attrs={"class": "profil-input"}),
            "content": forms.Textarea(attrs={"class": "text-input mt-2"}),
            "club": forms.Select(attrs={"class": "profil-select"}),
        }

    def __init__(self, user_id, *args, **kwargs):
        super(EditSondage, self).__init__(*args, **kwargs)
        self.fields["club"].choices = [("", "Élève")] + [
            (membership.club.id, membership.club)
            for membership in Membership.objects.filter(student__user__pk=user_id)
        ]

 """


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("post", "club", "content")
        widgets = {
            "club": forms.Select(attrs={"class": "profil-select"}),
        }

    def __init__(self, post_id, user_id, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields["club"].choices = [("", "Élève")] + [
            (membership.club.id, membership.club)
            for membership in Membership.objects.filter(student__user__pk=user_id)
        ]
        self.fields["post"].initial = post_id


class AddShotgun(forms.ModelForm):
    class Meta:
        model = Shotgun
        fields = (
            "club",
            "title",
            "content",
            "starting_date",
            "ending_date",
            "size",
            "requires_motivation",
            "success_message",
            "failure_message",
        )

        widgets = {
            "club": forms.Select(attrs={"class": "profil-select"}),
            "title": forms.TextInput(attrs={"class": "profil-input"}),
            "content": forms.Textarea(attrs={"class": "text-input mt-2"}),
            "starting_date": forms.DateTimeInput(attrs={"class": "profil-input"}),
            "ending_date": forms.DateTimeInput(attrs={"class": "profil-input"}),
            # "starting_date": forms.TextInput(attrs={"class": "profil-input"}),
            # "ending_date": forms.TextInput(attrs={"class": "profil-input"}),
            "size": forms.TextInput(attrs={"class": "profil-input"}),
            "success_message": forms.Textarea(attrs={"class": "text-input mt-2"}),
            "failure_message": forms.Textarea(attrs={"class": "text-input mt-2"}),
        }

    def __init__(self, clubs, *args, **kwargs):
        super(AddShotgun, self).__init__(*args, **kwargs)
        self.fields["club"].choices = []
        for club in clubs:
            self.fields["club"].choices.append((str(club.id), str(club.name)))
