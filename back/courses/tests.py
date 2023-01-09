from unittest.mock import MagicMock

from django.contrib.auth import models
from django.core.files import File
from django.test import TestCase
from django.utils import timezone
from news.models import Post
from social.models import Student

from .models import (
    Course,
    CourseDepartment,
    CourseUpdate,
    Enrolment,
    Group,
    Resource,
    Teacher,
)


class TeacherModelest(TestCase):
    def test_teacher_save_in_database(self):
        teacher = Teacher(name="Professeur")
        teacher.save()
        retrieved_teacher = Teacher.objects.get(pk=teacher.pk)
        self.assertEqual(retrieved_teacher.pk, teacher.pk)


class CourseModelTest(TestCase):
    def test_course_save_in_database(self):
        test_teacher = Teacher(name="Professeur")
        test_teacher.save()
        course = Course(
            name="Cours",
            acronym="ABC",
            department=CourseDepartment.AHE,
            teacher=test_teacher,
            description="Description",
        )
        course.save()
        retrieved_course = Course.objects.get(pk=course.pk)
        self.assertEqual(retrieved_course.pk, course.pk)


class CourseUpdateModelTest(TestCase):
    def test_course_update_save_in_database(self):
        test_teacher = Teacher(name="Professeur")
        test_teacher.save()
        test_old_course = Course(
            name="Ancien cours",
            acronym="ABC",
            department=CourseDepartment.AHE,
            teacher=test_teacher,
            description="Description",
        )
        test_old_course.save()
        test_new_course = Course(
            name="Nouveu cours",
            acronym="DEF",
            department=CourseDepartment.AHE,
            teacher=test_teacher,
            description="Nouvelle description",
        )
        test_new_course.save()
        course_update = CourseUpdate(
            date=timezone.now(),
            old_course=test_old_course,
            new_course=test_new_course,
        )
        course_update.save()
        retrieved_course_update = CourseUpdate.objects.get(pk=course_update.pk)
        self.assertEqual(retrieved_course_update.pk, course_update.pk)


class GroupModelTest:
    def group_save_in_database(self):
        test_teacher = Teacher(name="Professeur")
        test_teacher.save()
        test_course = Course(
            name="Cours",
            acronym="ABC",
            department=CourseDepartment.AHE,
            teacher=test_teacher,
            description="Description",
        )
        test_course.save()
        test_teacher = Teacher("Professeur")
        test_teacher.save()
        group = Group(
            course=test_course,
            teacher=test_teacher,
        )
        group.save()
        retrieved_group = Group.objects.get(pk=group.pk)
        self.assertEqual(retrieved_group.pk, group.pk)


class EnrolmentModelTest(TestCase):
    def test_enrolment_save_in_database(self):
        test_teacher = Teacher(name="Professeur")
        test_teacher.save()
        test_user = models.User(username="Utilisateur")
        test_user.save()
        test_course = Course(
            name="Cours",
            acronym="ABC",
            department=CourseDepartment.AHE,
            teacher=test_teacher,
            description="Description",
        )
        test_course.save()
        test_group = Group(
            course=test_course,
            teacher=test_teacher,
        )
        test_group.save()
        test_student = Student(
            user=test_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        test_student.save()
        enrolment = Enrolment(
            is_old=False,
            group=test_group,
            student=test_student,
        )
        enrolment.save()
        retrieved_enrolment = Enrolment.objects.get(pk=enrolment.pk)
        self.assertEqual(retrieved_enrolment.pk, enrolment.pk)


class ResourceModelTest(TestCase):
    def test_resource_saves_in_database(self):
        test_user = models.User()
        test_user.save()
        student = Student(
            user=test_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        student.save()

        post = Post(
            title="Title",
            author=student,
            date=timezone.now(),
            content="Lorem ipsum...",
        )
        post.save()

        file_mock = MagicMock(spec=File)
        file_mock.name = "filename.txt"

        resource = Resource(
            name="Name",
            author=student,
            date=timezone.now(),
            post=post,
            file=file_mock,
        )
        resource.save()

        retrieved_resource = Resource.objects.get(pk=resource.pk)

        self.assertEqual(retrieved_resource, resource)
