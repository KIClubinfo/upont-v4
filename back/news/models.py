from django.db import models
from django.utils import timezone
from social.models import Student


class Event(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    club = models.ForeignKey("social.Club", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField()
    location = models.CharField(max_length=50)
    participants = models.ManyToManyField(
        Student,
        related_name="events",
        blank=True,
    )
    shotgun = models.ForeignKey(
        "Shotgun", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey(
        "social.Membership", verbose_name="author", on_delete=models.SET_NULL, null=True
    )
    published_as_student = models.BooleanField()
    date = models.DateTimeField()
    illustration = models.ImageField(
        upload_to="post_illustrations", null=True, blank=True
    )
    content = models.TextField()
    event = models.ForeignKey("Event", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    author = models.ForeignKey(
        "social.Membership", verbose_name="author", on_delete=models.SET_NULL, null=True
    )
    published_as_student = models.BooleanField()
    date = models.DateTimeField()
    content = models.TextField()

    def __str__(self):
        return self.content


class Participation(models.Model):
    participant = models.ForeignKey("social.Student", on_delete=models.CASCADE)
    shotgun_date = models.DateTimeField()


class Shotgun(models.Model):
    title = models.CharField(max_length=50)
    club = models.ForeignKey(
        "social.Club",
        verbose_name="organizing club",
        on_delete=models.SET_NULL,
        null=True,
    )
    content = models.TextField()
    starting_date = models.DateTimeField()
    ending_date = models.DateTimeField()
    size = models.IntegerField(default=0)
    requires_motivation = models.BooleanField(default=False)
    participations = models.ManyToManyField(
        Participation,
        related_name="shotgun",
        blank=True,
    )

    def __str__(self):
        return self.title

    def accepted_participants(self):
        return self.participations.order_by("shotgun_date")[: self.size]

    def is_started(self):
        return timezone.now() > self.starting_date

    def is_ended(self):
        return timezone.now() > self.ending_date
