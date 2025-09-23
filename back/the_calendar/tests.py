import datetime

from django.contrib.auth import models
from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework.test import APITestCase

from courses.models import Course, Enrolment, Group, Teacher, Timeslot
from news.models import Event
from social.models import Student


class CalendarDataTest(APITestCase):
    url = reverse_lazy("calendar_data")

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

        # Add courses and timeslots
        self.teacher = Teacher(name="Dumbledore")
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

        self.group1 = Group(
            course=self.course1,
            teacher=self.teacher,
            number=12,
        )
        self.group1.save()

        self.group2 = Group(
            course=self.course2,
            teacher=self.teacher,
            number=42,
        )
        self.group2.save()

        self.timeslot1 = Timeslot(
            start=timezone.now(),
            end=timezone.now() + datetime.timedelta(hours=3),
            place="Tatooine",
        )
        self.timeslot1.save()
        self.timeslot1.course_groups.add(self.group1)

        self.timeslot2 = Timeslot(
            start=timezone.now(),
            end=timezone.now() + datetime.timedelta(hours=3),
            place="Coruscant",
        )
        self.timeslot2.save()
        self.timeslot2.course_groups.add(self.group2)

        # Add Events
        self.event1 = Event(
            name="Event 1",
            description="Event 1 description",
            date=timezone.now(),
            end=timezone.now() + datetime.timedelta(hours=1),
            location="Arkham",
        )
        self.event1.save()

        self.event2 = Event(
            name="Event 2",
            description="Event 2 description",
            date=timezone.now(),
            end=timezone.now() + datetime.timedelta(hours=2),
            location="Innsmouth",
        )
        self.event2.save()

    def test_data(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.url)

        # Check if the request was successful
        self.assertEqual(response.status_code, 200)
        # Check if everything has been sent
        self.assertEqual(len(response.data), 4)
        # Check timeslot1 data
        response_course1 = response.data[0]
        self.assertEqual(response_course1["id"], self.timeslot1.pk)
        self.assertEqual(response_course1["type"], "course")
        self.assertEqual(response_course1["title"], self.course1.name)
        self.assertEqual(
            response_course1["start"],
            self.timeslot1.start.astimezone().isoformat())
        self.assertEqual(
            response_course1["end"],
            self.timeslot1.end.astimezone().isoformat())
        # Check event1 data
        response_event1 = response.data[2]
        self.assertEqual(response_event1["id"], self.event1.pk)
        self.assertEqual(response_event1["type"], "event")
        self.assertEqual(response_event1["title"], self.event1.name)
        self.assertEqual(
            response_event1["start"], self.event1.date.astimezone().isoformat()
        )
        self.assertEqual(
            response_event1["end"], self.event1.end.astimezone().isoformat()
        )

    def test_is_enrolled_filter(self):
        # Enroll the student in course1 and event1
        self.event1.participants.add(self.student)
        enrolment = Enrolment(group=self.group1, student=self.student)
        enrolment.save()

        self.client.login(username=self.username, password=self.password)

        response_true = self.client.get(self.url + "?is_enrolled=true")
        response_false = self.client.get(self.url + "?is_enrolled=false")

        # Check is the requests were successful
        self.assertEqual(response_true.status_code, 200)
        self.assertEqual(response_false.status_code, 200)

        # Check response_true
        self.assertEqual(len(response_true.data), 2)
        response_true_timeslot = response_true.data[0]
        self.assertEqual(response_true_timeslot["type"], "course")
        self.assertEqual(response_true_timeslot["id"], self.timeslot1.pk)
        response_true_event = response_true.data[1]
        self.assertEqual(response_true_event["type"], "event")
        self.assertEqual(response_true_event["id"], self.event1.pk)

        # Check response_false
        self.assertEqual(len(response_false.data), 2)
        response_false_timeslot = response_false.data[0]
        self.assertEqual(response_false_timeslot["type"], "course")
        self.assertEqual(response_false_timeslot["id"], self.timeslot2.pk)
        response_false_event = response_false.data[1]
        self.assertEqual(response_false_event["type"], "event")
        self.assertEqual(response_false_event["id"], self.event2.pk)
