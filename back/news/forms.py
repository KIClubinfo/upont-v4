from django import forms
from news.models import Shotgun
from social.models import Club


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

    def __init__(self, clubs, *args, **kwargs):
        super(AddShotgun, self).__init__(*args, **kwargs)
        self.fields["club"].choices = []
        for club in clubs:
            self.fields["club"].choices.append((str(club.id), str(club.name)))
