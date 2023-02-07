from unittest.mock import MagicMock

from django.contrib.auth import models
from django.core.files import File
from django.test import TestCase
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from news.models import Post
from rest_framework.test import APITestCase
from social.models import Student

from .models import (
    Course,
    CourseDepartment,
    CourseUpdate,
    Enrolment,
    Group,
    Resource,
    Teacher,
    Timeslot,
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
            name="Nouveau cours",
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


class TimeslotModelTest(TestCase):
    def test_timeslot_saves_in_database(self):
        teacher = Teacher(name="Bob")
        teacher.save()

        course = Course(
            name="Cours",
            acronym="ABC",
            department="GMM",
            teacher=teacher,
        )
        course.save()

        group = Group(
            course=course,
            teacher=teacher,
        )
        group.save()

        timeslot = Timeslot(
            start=timezone.now(),
            end=timezone.now(),
            place="Emplacement",
        )
        timeslot.save()
        timeslot.course_groups.add(group)

        retrieved_timeslot = Timeslot.objects.get(pk=timeslot.pk)
        self.assertEqual(retrieved_timeslot, timeslot)


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


class ListCourseDepartmentsTest(APITestCase):
    def setUp(self):
        self.username = "user"
        self.email = "user@mail.com"
        self.password = "Follow the white rabbit"

        self.user = models.User.objects.create_user(
            self.username, self.email, self.password
        )

        self.student = Student(
            user=self.user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        self.student.save()

    def test_course_departements(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("course_department_list")
        response = self.client.get(url)

        # Check if the request was successful
        self.assertEqual(response.status_code, 200)
        # Check the received data
        self.assertEqual(response.data, CourseDepartment.values)


class CourseViewsetTest(APITestCase):
    url = reverse_lazy("course-list")

    def setUp(self):
        self.username = "user"
        self.email = "user@mail.com"
        self.password = "Follow the white rabbit"

        self.user = models.User.objects.create_user(
            self.username, self.email, self.password
        )

        self.student = Student(
            user=self.user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        self.student.save()

        self.teacher = Teacher(name="Frankenstein")
        self.teacher.save()

        self.course1 = Course(
            name="Course 1",
            acronym="C1",
            department="GMM",
            teacher=self.teacher,
            description="Course 1 description",
        )
        self.course1.save()

        self.course2 = Course(
            name="Course 2",
            acronym="C2",
            department="GMM",
            teacher=self.teacher,
            description="Course 2 description",
        )
        self.course2.save()

    def test_courses_list(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.url)

        # Check if the request was successful
        self.assertEqual(response.status_code, 200)
        # Check if all the courses are received
        self.assertEqual(response.data.get("count"), 2)
        # Check course1 data
        response_course1 = response.data.get("results")[0]
        self.assertEqual(response_course1["id"], self.course1.pk)
        self.assertEqual(response_course1["name"], self.course1.name)
        self.assertEqual(response_course1["acronym"], self.course1.acronym)
        self.assertEqual(response_course1["department"], self.course1.department)
        self.assertEqual(response_course1["teacher"]["id"], self.course1.teacher.pk)
        self.assertEqual(response_course1["description"], self.course1.description)

    def test_is_enrolled_filter(self):
        # Enroll the user in Course1
        group = Group(
            course=self.course1,
            teacher=self.teacher,
        )
        group.save()

        enrolment = Enrolment(group=group, student=self.student)
        enrolment.save()

        self.client.login(username=self.username, password=self.password)
        response_true = self.client.get(self.url + "?is_enrolled=true")
        response_false = self.client.get(self.url + "?is_enrolled=false")

        # Check if the requests was successful
        self.assertEqual(response_true.status_code, 200)
        self.assertEqual(response_false.status_code, 200)
        # Check response_true
        self.assertEqual(response_true.data.get("count"), 1)
        response_true_course = response_true.data.get("results")[0]
        self.assertEqual(response_true_course["id"], self.course1.pk)
        # Check response false
        self.assertEqual(response_false.data.get("count"), 1)
        response_false_course = response_false.data.get("results")[0]
        self.assertEqual(response_false_course["id"], self.course2.pk)
