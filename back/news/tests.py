import datetime

from django.contrib.auth import models
from django.test import TestCase
from django.utils import timezone
from social.models import Student

from .models import Participation, Shotgun


class ShotgunModelTest(TestCase):
    def create_two_students(self):
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
        return student1, student2

    def shotgun_with_two_participants_without_motivation(self):
        shotgun = Shotgun(
            title="Shotgun",
            content="Un shotgun",
            starting_date=timezone.now(),
            ending_date=timezone.now() + datetime.timedelta(days=1),
            size=1,
        )
        shotgun.save()
        student1, student2 = self.create_two_students()
        participation1 = Participation(
            shotgun=shotgun, participant=student1, shotgun_date=timezone.now()
        )
        participation2 = Participation(
            shotgun=shotgun,
            participant=student2,
            shotgun_date=timezone.now() + datetime.timedelta(seconds=1),
        )
        participation1.save()
        participation2.save()
        return shotgun, participation1, participation2

    def shotgun_with_two_participants_with_motivation(self):
        shotgun = Shotgun(
            title="Shotgun",
            content="Un shotgun",
            starting_date=timezone.now(),
            ending_date=timezone.now() + datetime.timedelta(days=1),
            size=1,
            requires_motivation=True,
        )
        shotgun.save()
        student1, student2 = self.create_two_students()
        participation1 = Participation(
            shotgun=shotgun,
            participant=student1,
            shotgun_date=timezone.now(),
            motivation="Motivation de l'élève 1.",
        )
        participation2 = Participation(
            shotgun=shotgun,
            participant=student2,
            shotgun_date=timezone.now() + datetime.timedelta(seconds=1),
            motivation="Motivation de l'élève 2.",
        )
        participation1.save()
        participation2.save()
        return shotgun, participation1, participation2

    def test_shotgun_saves_in_database(self):
        shotgun = Shotgun(
            title="Shotgun",
            content="Un shotgun",
            starting_date=timezone.now(),
            ending_date=timezone.now() + datetime.timedelta(days=1),
            size=1,
        )
        shotgun.save()
        retrieved_shotgun = Shotgun.objects.get(pk=shotgun.pk)
        self.assertEqual(retrieved_shotgun.pk, shotgun.pk)

    def test_shotgun_started(self):
        shotgun = Shotgun(
            title="Shotgun",
            content="Un shotgun",
            starting_date=timezone.now(),
            ending_date=timezone.now() + datetime.timedelta(days=1),
            size=1,
        )
        self.assertTrue(shotgun.is_started())

    def test_shotgun_not_started(self):
        shotgun = Shotgun(
            title="Shotgun",
            content="Un shotgun",
            starting_date=timezone.now() + datetime.timedelta(seconds=1),
            ending_date=timezone.now() + datetime.timedelta(days=1),
            size=1,
        )
        self.assertFalse(shotgun.is_started())

    def test_shotgun_ended(self):
        shotgun = Shotgun(
            title="Shotgun",
            content="Un shotgun",
            starting_date=timezone.now(),
            ending_date=timezone.now(),
            size=1,
        )
        self.assertTrue(shotgun.is_ended())

    def test_shotgun_not_ended(self):
        shotgun = Shotgun(
            title="Shotgun",
            content="Un shotgun",
            starting_date=timezone.now(),
            ending_date=timezone.now() + datetime.timedelta(seconds=10),
            size=1,
        )
        self.assertFalse(shotgun.is_ended())

    def test_function_participations_without_motivation(self):
        (
            shotgun,
            participation1,
            participation2,
        ) = self.shotgun_with_two_participants_without_motivation()
        self.assertTrue(len(shotgun.participations()) == 2)

    def test_function_participations_with_motivation(self):
        (
            shotgun,
            participation1,
            participation2,
        ) = self.shotgun_with_two_participants_with_motivation()
        self.assertTrue(len(shotgun.participations()) == 2)

    def test_get_right_accepted_participants_without_motivation(self):
        (
            shotgun,
            participation1,
            participation2,
        ) = self.shotgun_with_two_participants_without_motivation()
        self.assertTrue(shotgun.accepted_participations()[0] == participation1)
        self.assertTrue(len(shotgun.accepted_participations()) == 1)
        shotgun.size = 2
        self.assertTrue(shotgun.accepted_participations()[0] == participation1)
        self.assertTrue(shotgun.accepted_participations()[1] == participation2)
        self.assertTrue(len(shotgun.accepted_participations()) == 2)
        shotgun.size = 3
        self.assertTrue(shotgun.accepted_participations()[0] == participation1)
        self.assertTrue(shotgun.accepted_participations()[1] == participation2)
        self.assertTrue(len(shotgun.accepted_participations()) == 2)

    def test_get_right_accepted_participants_with_motivation(self):
        (
            shotgun,
            participation1,
            participation2,
        ) = self.shotgun_with_two_participants_with_motivation()
        # works the same as without motivation if all motivations are accepted :
        self.assertTrue(shotgun.accepted_participations()[0] == participation1)
        self.assertTrue(len(shotgun.accepted_participations()) == 1)
        shotgun.size = 2
        self.assertTrue(shotgun.accepted_participations()[0] == participation1)
        self.assertTrue(shotgun.accepted_participations()[1] == participation2)
        self.assertTrue(len(shotgun.accepted_participations()) == 2)
        shotgun.size = 3
        self.assertTrue(shotgun.accepted_participations()[0] == participation1)
        self.assertTrue(shotgun.accepted_participations()[1] == participation2)
        self.assertTrue(len(shotgun.accepted_participations()) == 2)
        # new test cases :
        shotgun.size = 1
        participation1.failed_motivation = True
        participation1.save()
        self.assertTrue(shotgun.accepted_participations()[0] == participation2)
        self.assertTrue(len(shotgun.accepted_participations()) == 1)
        participation1.failed_motivation = False
        participation2.failed_motivation = True
        participation1.save()
        participation2.save()
        self.assertTrue(shotgun.accepted_participations()[0] == participation1)
        self.assertTrue(len(shotgun.accepted_participations()) == 1)
        participation1.failed_motivation = True
        participation1.save()
        self.assertTrue(len(shotgun.accepted_participations()) == 0)

    def test_function_participated_without_motivation(self):
        (
            shotgun,
            participation1,
            participation2,
        ) = self.shotgun_with_two_participants_without_motivation()
        self.assertTrue(shotgun.participated(participation1.participant))
        test_user = models.User(username="user")
        test_user.save()
        student = Student(
            user=test_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        student.save()
        self.assertFalse(shotgun.participated(student))

    def test_function_participated_with_motivation(self):
        (
            shotgun,
            participation1,
            participation2,
        ) = self.shotgun_with_two_participants_with_motivation()
        self.assertTrue(shotgun.participated(participation1.participant))
        participation2.failed_motivation = True
        participation2.save()
        self.assertTrue(shotgun.participated(participation2.participant))
        test_user = models.User(username="user")
        test_user.save()
        student = Student(
            user=test_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        student.save()
        self.assertFalse(shotgun.participated(student))

    def test_function_got_accepted(self):
        (
            shotgun,
            participation1,
            participation2,
        ) = self.shotgun_with_two_participants_without_motivation()
        self.assertTrue(shotgun.got_accepted(participation1.participant))
        self.assertFalse(shotgun.got_accepted(participation2.participant))
        test_user = models.User(username="user")
        test_user.save()
        student = Student(
            user=test_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        student.save()
        self.assertFalse(shotgun.got_accepted(student))
