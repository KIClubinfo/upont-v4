from django import forms
from social.models import Membership

from .models import Event, Post


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
            "published_as_student",
            "author",
        )

    def __init__(self, user_id, *args, **kwargs):
        super(EditPost, self).__init__(*args, **kwargs)
        self.fields["author"].choices = [
            (membership.id, membership.club)
            for membership in Membership.objects.filter(student__user__pk=user_id)
        ]
