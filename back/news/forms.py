from django import forms
from social.models import Membership

from .models import Event, Post, Comment


class EditEvent(forms.ModelForm):
    class Meta:
        model = Event
        fields = ("name", "description", "date", "location", "poster", "club")

    def __init__(self, user_id, *args, **kwargs):
        super(EditEvent, self).__init__(*args, **kwargs)
        self.fields["club"].choices = [
            (membership.club.id, membership.club)
            for membership in Membership.objects.filter(student__user__pk=user_id)
        ]


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
            "club": forms.Select(attrs={"class": ""}),
            "content": forms.Textarea(attrs={"class": "news-card-edit-comment-input"}),
        }

    def __init__(self, post_id, user_id, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields["club"].choices = [("", "Élève")] + [
            (membership.club.id, membership.club)
            for membership in Membership.objects.filter(student__user__pk=user_id)
        ]
        self.fields["post"].initial = post_id
