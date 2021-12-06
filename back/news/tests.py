import datetime

from django.contrib.auth import models
from django.test import TestCase
from django.utils import timezone
from social.models import Student

from .models import Participation, Shotgun


class ShotgunModelTest(TestCase):
    def test_shotgun_saves_in_database(self):
        shotgun = Shotgun(
            title="Shotgun", content="Un shotgun", date=timezone.now(), size=1
        )
        shotgun.save()
        retrieved_shotgun = Shotgun.objects.get(pk=shotgun.pk)
        self.assertEqual(retrieved_shotgun.pk, shotgun.pk)

    def test_shotgun_started(self):
        shotgun = Shotgun(
            title="Shotgun", content="Un shotgun", date=timezone.now(), size=1
        )
        self.assertTrue(shotgun.is_started())

    def test_shotgun_not_started(self):
        shotgun = Shotgun(
            title="Shotgun",
            content="Un shotgun",
            date=timezone.now() + datetime.timedelta(seconds=1),
            size=1,
        )
        self.assertFalse(shotgun.is_started())

    def test_get_right_participants(self):
        shotgun = Shotgun(
            title="Shotgun", content="Un shotgun", date=timezone.now(), size=1, id=1
        )
        shotgun.save()
        test_user1 = models.User(username="user1")
        test_user1.save()
        student1 = Student(
            user=test_user1,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        student1.save()
        test_user2 = models.User(username="user2")
        test_user2.save()
        student2 = Student(
            user=test_user2,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        student2.save()
        participation1 = Participation(
            participant=student1, shotgun_date=timezone.now()
        )
        participation2 = Participation(
            participant=student2,
            shotgun_date=timezone.now() + datetime.timedelta(seconds=1),
        )
        participation1.save()
        participation2.save()
        shotgun.participations.add(participation1)
        shotgun.participations.add(participation2)
        self.assertTrue(shotgun.accepted_participants()[0] == participation1)
        self.assertTrue(len(shotgun.accepted_participants()) == 1)
