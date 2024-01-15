from django import forms


class FileAndDatesForm(forms.Form):
    class Meta:
        fields = (
            "file",
            "openDate",
            "closeDate",
            "pickupDate",
        )
        widgets = {
            "file" : forms.FileInput(attrs={"class" : "button blue-button"}),
            "openDate" : forms.DateInput(attrs={"class" : "button blue-button"}),
            "closeDate" : forms.DateInput(attrs={"class" : "button blue-button"}),
            "pickupDate" : forms.DateInput(attrs={"class" : "button blue-button"})
        }

    def is_valid(self) -> bool:
        return super().is_valid()