from django.contrib.auth import models
from django.core.validators import ValidationError
from django.test import TestCase

from .models import Category, Club, Membership, Nationality, Promotion, Role, Student


class PromotionModelTest(TestCase):
    def test_promotion_saves_in_database(self):
        promotion = Promotion(year=2023, name="Promonavirus", nickname="023")
        promotion.save()
        retrieved_promotion = Promotion.objects.get(pk=promotion.pk)
        self.assertEqual(retrieved_promotion.pk, promotion.pk)


class NationalityModelTest(TestCase):
    def test_nationality_saves_in_database(self):
        nationality = Nationality(nationality="Française", short_nationality="FR")
        nationality.save()
        retrieved_nationality = Nationality.objects.get(pk=nationality.pk)
        self.assertEqual(retrieved_nationality.pk, nationality.pk)


class RoleModelTest(TestCase):
    def test_role_saves_in_database(self):
        role = Role(name="Membre")
        role.save()
        retrieved_role = Role.objects.get(pk=role.pk)
        self.assertEqual(retrieved_role.pk, role.pk)


class StudentModelTest(TestCase):
    def test_student_saves_in_database(self):
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
        retrieved_student = Student.objects.get(pk=student.pk)
        self.assertEqual(retrieved_student.pk, student.pk)

    def test_student_rejects_wrong_phone_number(self):
        test_user = models.User()
        test_user.save()
        student = Student(
            user=test_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="test",
        )
        self.assertRaises(ValidationError, student.full_clean)


class CategoryModelTest(TestCase):
    def test_category_saves_in_database(self):
        category = Category(name="Test")
        category.save()
        retrieved_category = Category.objects.get(pk=category.pk)
        self.assertEqual(retrieved_category.pk, category.pk)


class ClubModelTest(TestCase):
    def test_club_saves_in_database(self):
        club = Club(description="Un Club", active=True, has_fee=True)
        club.save()
        retrieved_club = Club.objects.get(pk=club.pk)
        self.assertEqual(retrieved_club.pk, club.pk)
    
    def test_function_is_member(self):
        test_user = models.User()
        test_user.save()
        test_student = Student(
            user=test_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        test_student.save()
        test_club = Club(description="Un Club", active=True, has_fee=True)
        test_club.save()
        self.assertFalse(test_club.is_member(test_student.id))
        membership = Membership(is_admin=False, club=test_club, student=test_student)
        membership.save()
        self.assertTrue(test_club.is_member(test_student.id))
    
    def test_function_is_admin(self):
        test_user = models.User()
        test_user.save()
        test_student = Student(
            user=test_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        test_student.save()
        test_club = Club(description="Un Club", active=True, has_fee=True)
        test_club.save()
        self.assertFalse(test_club.is_admin(test_student.id))
        membership = Membership(is_admin=False, club=test_club, student=test_student)
        membership.save()
        self.assertFalse(test_club.is_admin(test_student.id))
        membership.is_admin = True
        membership.save()
        self.assertTrue(test_club.is_admin(test_student.id))


class MembershipModelTest(TestCase):
    def test_membership_saves_in_database(self):
        test_user = models.User()
        test_user.save()
        test_student = Student(
            user=test_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        test_student.save()
        test_club = Club(description="Un Club", active=True, has_fee=True)
        test_club.save()
        membership = Membership(is_admin=False, club=test_club, student=test_student)
        membership.save()
        retrieved_membership = Membership.objects.get(pk=membership.pk)
        self.assertEqual(retrieved_membership.pk, membership.pk)
