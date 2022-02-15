from django import forms
from django.shortcuts import get_object_or_404
from social.models import Membership, Student

from .models import Comment, Event, Post, Shotgun


class EditEvent(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            "name",
            "description",
            "date",
            "location",
            "poster",
            "club",
            "shotgun",
        )
        widgets = {
            "name": forms.TextInput(attrs={"class": "profil-input"}),
            "description": forms.Textarea(attrs={"class": "profil-input"}),
            "date": forms.TextInput(attrs={"class": "profil-input"}),
            "location": forms.TextInput(attrs={"class": "profil-input"}),
            "poster": forms.FileInput(attrs={"class": "profil-input"}),
            "club": forms.Select(attrs={"class": "profil-select"}),
            "shotgun": forms.Select(attrs={"class": "profil-select"}),
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
            "content": forms.Textarea(attrs={"class": "profil-input"}),
            "event": forms.Select(attrs={"class": "profil-select"}),
            "club": forms.Select(attrs={"class": "profil-select"}),
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
        )
        widgets = {
            "club": forms.Select(attrs={"class": "profil-select"}),
            "title": forms.TextInput(attrs={"class": "profil-input"}),
            "content": forms.TextInput(attrs={"class": "profil-input"}),
            "starting_date": forms.TextInput(attrs={"class": "profil-input"}),
            "ending_date": forms.TextInput(attrs={"class": "profil-input"}),
            "size": forms.TextInput(attrs={"class": "profil-input"}),
        }

    def __init__(self, clubs, *args, **kwargs):
        super(AddShotgun, self).__init__(*args, **kwargs)
        self.fields["club"].choices = []
        for club in clubs:
            self.fields["club"].choices.append((str(club.id), str(club.name)))
