from django.db import models
from django.utils.translation import gettext_lazy as _

from news.models import Post
from social.models import Student


class Teacher(models.Model):
    name = models.CharField(max_length=100, default="Professeur anonyme")

    def __str__(self):
        return self.name


class CourseDepartment(models.TextChoices):
    IMI = "IMI", _("Ingénierie mathématique et informatique")
    GCC = "GCC", _("Génie civil et construction")
    GMM = "GMM", _("Génie mécanique et matériaux")
    SEGF = "SEGF", _("Sciences économiques, gestion, finance")
    VET = "VET", _("Ville, environnement, transport")
    GI = "GI", _("Génie industriel")
    A1 = "1A", _("Première année")
    DE = "DE", _("Direction de l'enseignement")
    DLC = "DLC", _("Département langues et culture")
    SHS = "SHS", _("Sciences humaines et sociales")
    PAPDD = "PAPDD", _(
        "Politique et action publique pour le développement durable")
    DS = "D.SCHOOL", _("d.school")
    AHE = "AHE", _("Autres hors école")


class Course(models.Model):
    name = models.CharField(max_length=100, default="Cours sans nom")
    acronym = models.CharField(max_length=100, default="ABC")
    department = models.CharField(
        max_length=8,
        choices=CourseDepartment.choices,
        default=CourseDepartment.AHE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)

    description = models.TextField()
    old_courses = models.ManyToManyField(
        "self",
        through="CourseUpdate",
        symmetrical=False,
        related_name="new_courses",
        blank=True,
    )
    posts = models.ManyToManyField(
        Post,
        related_name="course",
        blank=True,
    )

    def __str__(self):
        return self.name


class CourseUpdate(models.Model):
    date = models.DateTimeField()
    old_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="old")
    new_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="new")

    def __str__(self):
        return self.old_course.name + " : " + self.new_course.name


class Group(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="groups")
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="groups"
    )
    number = models.IntegerField(blank=True, null=True)
    students = models.ManyToManyField(
        Student,
        through="Enrolment",
        related_name="course",
        blank=True,
    )

    def __str__(self):
        if self.number is None:
            return "{} : {}".format(self.course.name, self.teacher.name)
        else:
            return "{} ({}) : {}".format(
                self.course.name, self.number, self.teacher.name
            )


class Enrolment(models.Model):
    is_old = models.BooleanField(default=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return self.group.course.name + " : " + self.student.user.username


class Timeslot(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    course_groups = models.ManyToManyField(
        Group, related_name="timeslot", blank=True)
    place = models.CharField(max_length=50, blank=True)

    def get_course_name(self):
        """
        Return the name of the corresponding course
        Return None if it is attached to no course
        """
        if self.course_groups.exists():
            course_name = self.course_groups.first().course.name
        else:
            course_name = None

        return course_name


class Resource(models.Model):
    name = models.CharField(max_length=50, default="Ressource")
    author = models.ForeignKey(
        "social.Student",
        verbose_name="author",
        on_delete=models.SET_NULL,
        null=True)
    date = models.DateTimeField()
    file = models.FileField(
        "Fichier",
        upload_to="ressources",
        null=True,
        blank=True)
    post = models.ForeignKey(
        "news.Post",
        verbose_name="post",
        on_delete=models.CASCADE,
        null=True,
        related_name="resource",
    )
