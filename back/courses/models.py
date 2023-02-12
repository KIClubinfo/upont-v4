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
    PAPDD = "PAPDD", _("Politique et action publique pour le développement durable")
    DS = "D.SCHOOL", _("d.school")
    AHE = "AHE", _("Autres hors école")


class Course(models.Model):
    name = models.CharField(max_length=100, default="Cours sans nom")
    acronym = models.CharField(max_length=100, default="ABC")
    department = models.CharField(
        max_length=8, choices=CourseDepartment.choices, default=CourseDepartment.AHE
    )
    teacher = models.ManyToManyField(
        Teacher, 
        related_name="courses",
        blank=True,
        )
        
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
    old_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="old")
    new_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="new")

    def __str__(self):
        return self.old_course.name + " : " + self.new_course.name


class Group(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    students = models.ManyToManyField(
        Student,
        through="Enrolment",
        related_name="course",
        blank=True,
    )

    def __str__(self):
        return self.course.name + " : " + self.teacher.name


class Enrolment(models.Model):
    is_old = models.BooleanField(default=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return self.group.course.name + " : " + self.student.user.username
