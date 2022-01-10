from django import forms
from django.core.validators import RegexValidator

from .models import Event, Post


class EditEvent(forms.ModelForm):
    class Meta:
        model = Event
        fields = ("name", "description", "date", "location", "poster")
