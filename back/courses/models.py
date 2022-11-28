from courses.models import Course
from django.db import models
from news.models import Post
from social.models import Student


class Update(models.Model):
    date = models.DateTimeField()
    old_course = models.ForeignKey(Course, on_delete=models.CASCADE)
    new_course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.old_course.name + " : " + self.new_course.name


class Course(models.Model):
    name = models.CharField(max_length=100, default="Cours inconnu")
    acronym = models.CharField(max_length=100, default="ABC")
    department = models.CharField(
        max_length=4, choices=Student.Department.choices, default=Student.Department.A1
    )
    description = models.TextField()
    old_courses = models.ManyToManyField(
        Course,
        through="Update",
        related_name="new_courses",
        blank=True,
    )
    posts = models.ManyToManyField(
        Post,
        related_name="course",
        blank=True,
    )


class Teacher(models.Model):
    name = models.CharField(max_length=100, default="Professeur inconnu")


class Enrolment(models.Model):
    is_old = models.BooleanField(default=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return self.course.name + " : " + self.student.user.username


class Group(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    students = models.ManyToManyField(
        Student,
        through="Enrolment",
        related_name="course",
        blank=True,
    )
