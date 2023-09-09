from django.db import models
from django.db.models import F
from django.db.models.expressions import Window
from django.db.models.functions import Rank
from django.utils import timezone
from social.models import Student


class Event(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    club = models.ForeignKey("social.Club", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField()
    end = models.DateTimeField()
    location = models.CharField(max_length=50)
    participants = models.ManyToManyField(
        Student,
        related_name="events",
        blank=True,
    )
    poster = models.ImageField(upload_to="poster", null=True, blank=True)
    shotgun = models.ForeignKey(
        "Shotgun", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey(
        "social.Student", verbose_name="author", on_delete=models.SET_NULL, null=True
    )
    club = models.ForeignKey(
        "social.Club", on_delete=models.SET_NULL, null=True, blank=True
    )
    date = models.DateTimeField()
    illustration = models.ImageField(
        upload_to="post_illustrations", null=True, blank=True
    )
    content = models.TextField()
    event = models.ForeignKey("Event", on_delete=models.SET_NULL, null=True, blank=True)
    likes = models.ManyToManyField(
        Student,
        related_name="posts",
        blank=True,
        editable=False,
    )
    dislikes = models.ManyToManyField(
        Student,
        related_name="post_dislikes",
        blank=True,
        editable=False,
    )

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()

    def total_comments(self):
        return self.comments.count()


class Comment(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        "social.Student", verbose_name="author", on_delete=models.SET_NULL, null=True
    )
    club = models.ForeignKey(
        "social.Club", on_delete=models.SET_NULL, null=True, blank=True
    )
    date = models.DateTimeField()
    content = models.TextField()

    def __str__(self):
        author = [self.author, self.club][bool(self.club)]
        return f"Comment from {author}: '{self.content}'"


class Participation(models.Model):
    participant = models.ForeignKey("social.Student", on_delete=models.CASCADE)
    shotgun = models.ForeignKey("Shotgun", on_delete=models.CASCADE, null=True)
    shotgun_date = models.DateTimeField()
    motivation = models.TextField(null=True)
    failed_motivation = models.BooleanField(default=False)


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
    motivations_review_finished = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def participations(self):
        participations = Participation.objects.filter(shotgun=self).annotate(
            rank=Window(expression=Rank(), order_by=F("shotgun_date").asc()),
        )
        return participations

    def accepted_participations(self):
        participations = Participation.objects.filter(
            shotgun=self, failed_motivation=False
        )
        return participations.order_by("shotgun_date")[: self.size]

    def is_started(self):
        return timezone.now() > self.starting_date

    def is_ended(self):
        if self.ending_date is None:
            return False
        return timezone.now() > self.ending_date

    def participated(self, student: Student):
        participation = Participation.objects.filter(shotgun=self, participant=student)
        if participation.exists():
            return True
        return False

    def got_accepted(self, student: Student):  # Complexité dégueulasse
        for participation in self.accepted_participations():
            if participation.participant == student:
                return True
        return False
