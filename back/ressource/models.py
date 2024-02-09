from django.db import models


class Logo(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=5)
    image = models.ImageField(upload_to="logos/")
    category = models.CharField(max_length=100, null=True, blank=True)
    # Add other fields as needed

    def __str__(self):
        return self.name
