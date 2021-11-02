from django.db import models
from social.models import Student


class Event(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    club = models.ForeignKey("Club", on_delete=models.CASCADE)
    date = models.DateTimeField()
    location = models.CharField(max_length=50)
    participants = models.ManyToManyField(
        Student,
        related_name="events",
        blank=True,
    )

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey("Club", verbose_name="author club", on_delete=models.CASCADE)
    date = models.DateTimeField()
    illustration = models.ImageField(upload_to="post_illustrations", null=True, blank=True)
    content = models.TextField()
    event = models.ForeignKey("Event", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    author = models.ForeignKey("Student", on_delete=models.CASCADE)
    date = models.DateTimeField()
    content = models.TextField()
    
    def __str__(self):
        return self.content


class Shotgun(models.Model):
    title = models.CharField(max_length=50)
    club = models.ForeignKey("Club", verbose_name="organizing club", on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField()
    size = models.IntegerField(default=0)
    requires_motivation = models.BooleanField(default=False)
    winners = models.ManyToManyField(
        Student,
        through="ShotgunResults",
        related_name="successful shotguns",
        blank=True,
    )

    def __str__(self):
        return self.title


class ShotgunResults(models.Model):
    shotgun = models.ForeignKey(Shotgun, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    position = models.IntegerField()
    date = models.DateTimeField()
    motivation = models.TextField()

    def __str__(self):
        return self.shotgun.title + " : " + self.student.user.username
