from django.contrib.auth import models
from django.core.validators import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import os
import base64

from trade.models import Good, Price, Transaction

from .models import (
    Category,
    Channel,
    ChannelJoinRequest,
    Club,
    Membership,
    Message,
    Nationality,
    Promotion,
    Role,
    Student,
)


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
            birthdate="2000-01-01",
            biography="Je suis un test",
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
            birthdate="01/01/2000",
            biography="Je suis un test",
        )
        self.assertRaises(ValidationError, student.full_clean)

    def test_student_rejects_wrong_birthdate(self):
        test_user = models.User()
        test_user.save()
        student = Student(
            user=test_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
            birthdate="01.0.000",
            biography="Je suis un test",
        )
        self.assertRaises(ValidationError, student.full_clean)

    fixtures = ["test_trade.json"]

    def test_balance_in_cents(self):
        student = Student.objects.get(pk=1)
        self.assertEqual(-500, student.balance_in_cents())
        club = Club.objects.get(pk=1)
        good = Good(name="test_provision_account", club=club)
        good.save()
        price = Price(good=good, price=-50, date=timezone.now())
        price.save()
        transaction = Transaction(
            good=good, quantity=1, student=student, date=timezone.now()
        )
        transaction.save()
        self.assertEqual(-450, student.balance_in_cents())
        self.assertEqual(-450, student.balance_in_cents(club))

    def test_balance_in_cents_specified_club(self):
        student = Student.objects.get(pk=1)
        club1 = Club.objects.get(pk=1)
        self.assertEqual(-500, student.balance_in_cents(club1))
        club2 = Club(description="Un 2e Club", active=True, has_fee=True)
        club2.save()
        good = Good(name="test_provision_account", club=club2)
        good.save()
        price = Price(good=good, price=-50, date=timezone.now())
        price.save()
        transaction = Transaction(
            good=good, quantity=1, student=student, date=timezone.now()
        )
        transaction.save()
        self.assertEqual(-500, student.balance_in_cents(club1))
        self.assertEqual(50, student.balance_in_cents(club2))

    def test_balance_in_euros(self):
        student = Student.objects.get(pk=1)
        self.assertEqual(-5, student.balance_in_euros())
        club = Club.objects.get(pk=1)
        good = Good(name="test_provision_account", club=club)
        good.save()
        price = Price(good=good, price=-50, date=timezone.now())
        price.save()
        transaction = Transaction(
            good=good, quantity=1, student=student, date=timezone.now()
        )
        transaction.save()
        self.assertEqual(-4.5, student.balance_in_euros())


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

    fixtures = ["test_trade.json"]

    def test_balance_in_cents(self):
        club = Club.objects.get(pk=1)
        self.assertEqual(500, club.balance_in_cents())
        student = Student.objects.get(pk=1)
        good = Good(name="test_provision_account", club=club)
        good.save()
        price = Price(good=good, price=-50, date=timezone.now())
        price.save()
        transaction = Transaction(
            good=good, quantity=1, student=student, date=timezone.now()
        )
        transaction.save()
        self.assertEqual(450, club.balance_in_cents())

    def test_balance_in_euros(self):
        club = Club.objects.get(pk=1)
        self.assertEqual(5, club.balance_in_euros())
        student = Student.objects.get(pk=1)
        good = Good(name="test_provision_account", club=club)
        good.save()
        price = Price(good=good, price=-50, date=timezone.now())
        price.save()
        transaction = Transaction(
            good=good, quantity=1, student=student, date=timezone.now()
        )
        transaction.save()
        self.assertEqual(4.5, club.balance_in_euros())


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


def _generate_public_key():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")


class ChannelMessagingApiTest(APITestCase):
    def setUp(self):
        self.user_1 = models.User.objects.create_user(
            username="user1",
            password="pw",
            first_name="Alice",
            last_name="Martin",
        )
        self.user_2 = models.User.objects.create_user(username="user2", password="pw")
        self.user_3 = models.User.objects.create_user(username="user3", password="pw")

        self.student_1 = Student.objects.create(
            user=self.user_1,
            public_key=_generate_public_key(),
        )
        self.student_2 = Student.objects.create(
            user=self.user_2,
            public_key=_generate_public_key(),
        )
        self.student_3 = Student.objects.create(
            user=self.user_3,
            public_key=_generate_public_key(),
        )

    def test_create_channel_stores_member_encrypted_keys(self):
        self.client.force_authenticate(user=self.user_1)
        response = self.client.post(
            reverse("create_channel"),
            {
                "name": "crypto-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        channel = Channel.objects.get(pk=response.data["channel_id"])
        self.assertEqual(channel.members.count(), 2)
        self.assertEqual(channel.admins.count(), 1)
        self.assertEqual(channel.encrypted_keys.count(), 2)
        self.assertEqual(
            channel.encrypted_keys.filter(student=self.student_1).count(),
            1,
        )
        self.assertEqual(
            channel.encrypted_keys.filter(student=self.student_2).count(),
            1,
        )

    def test_channel_key_endpoint_requires_membership(self):
        channel = Channel.objects.create(
            name="restricted-room",
            date=timezone.now(),
            creator=self.student_1,
        )
        channel.members.set([self.student_1, self.student_2])

        self.client.force_authenticate(user=self.user_3)
        response = self.client.get(
            reverse("channel_encrypted_key", kwargs={"channel_id": channel.id})
        )
        self.assertEqual(response.status_code, 403)

    def test_member_can_create_and_read_message(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "msg-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        create_message_response = self.client.post(
            reverse("create_message"),
            {
                "channel": channel_id,
                "by_club": "-1",
                "content": "ciphertext-placeholder",
            },
            format="json",
        )
        self.assertEqual(create_message_response.status_code, 201)
        self.assertEqual(
            Message.objects.filter(channel_id=channel_id).count(),
            1,
        )

        get_messages_response = self.client.get(
            reverse("channel_messages", kwargs={"channel_id": channel_id})
        )
        self.assertEqual(get_messages_response.status_code, 200)
        self.assertEqual(len(get_messages_response.data["messages"]), 1)
        self.assertEqual(
            get_messages_response.data["messages"][0]["content"],
            "ciphertext-placeholder",
        )
        self.assertEqual(
            get_messages_response.data["messages"][0]["author_name"],
            "Alice Martin",
        )

    def test_club_admin_can_send_message_as_club(self):
        club = Club.objects.create(
            name="Club Test",
            description="Club test",
            active=True,
            has_fee=False,
        )
        Membership.objects.create(
            student=self.student_1,
            club=club,
            role=None,
            is_admin=True,
            is_old=False,
        )
        Membership.objects.create(
            student=self.student_2,
            club=club,
            role=None,
            is_admin=False,
            is_old=False,
        )

        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "club-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": str(club.id),
            },
            format="json",
        )
        self.assertEqual(create_channel_response.status_code, 201)
        channel_id = create_channel_response.data["channel_id"]

        create_message_response = self.client.post(
            reverse("create_message"),
            {
                "channel": channel_id,
                "by_club": True,
                "content": "club-signed-message",
            },
            format="json",
        )
        self.assertEqual(create_message_response.status_code, 201)
        message = Message.objects.get(pk=create_message_response.data["message_id"])
        self.assertEqual(message.club_id, club.id)

    def test_non_club_admin_cannot_send_message_as_club(self):
        club = Club.objects.create(
            name="Club Test",
            description="Club test",
            active=True,
            has_fee=False,
        )
        Membership.objects.create(
            student=self.student_1,
            club=club,
            role=None,
            is_admin=True,
            is_old=False,
        )
        Membership.objects.create(
            student=self.student_2,
            club=club,
            role=None,
            is_admin=False,
            is_old=False,
        )

        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "club-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": str(club.id),
            },
            format="json",
        )
        self.assertEqual(create_channel_response.status_code, 201)
        channel_id = create_channel_response.data["channel_id"]

        self.client.force_authenticate(user=self.user_2)
        create_message_response = self.client.post(
            reverse("create_message"),
            {
                "channel": channel_id,
                "by_club": True,
                "content": "unauthorized-club-message",
            },
            format="json",
        )
        self.assertEqual(create_message_response.status_code, 403)

    def test_set_and_get_public_key(self):
        self.client.force_authenticate(user=self.user_1)
        new_public_key = _generate_public_key()
        set_response = self.client.post(
            reverse("student_public_key"),
            {"public_key": new_public_key},
            format="json",
        )
        self.assertEqual(set_response.status_code, 200)

        get_response = self.client.get(reverse("student_public_key"))
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.data["public_key"], new_public_key)

    def test_channels_list_contains_member_channel(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "list-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        self.assertEqual(create_channel_response.status_code, 201)

        list_response = self.client.get(reverse("channels_list"))
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data["channels"]), 1)
        self.assertEqual(list_response.data["channels"][0]["name"], "list-room")
        self.assertTrue(list_response.data["channels"][0]["has_encrypted_key"])

    def test_club_channel_requires_club_admin_and_is_unique(self):
        club = Club.objects.create(
            name="Club Test",
            description="Club test",
            active=True,
            has_fee=False,
        )
        Membership.objects.create(
            student=self.student_1,
            club=club,
            role=None,
            is_admin=True,
            is_old=False,
        )

        self.client.force_authenticate(user=self.user_1)
        first_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "club-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": str(club.id),
            },
            format="json",
        )
        self.assertEqual(first_response.status_code, 201)

        second_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "club-room-2",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": str(club.id),
            },
            format="json",
        )
        self.assertEqual(second_response.status_code, 400)
        self.assertEqual(
            second_response.data["error"], "Un channel existe deja pour ce club."
        )

    def test_non_admin_cannot_create_club_channel(self):
        club = Club.objects.create(
            name="Club Test",
            description="Club test",
            active=True,
            has_fee=False,
        )
        Membership.objects.create(
            student=self.student_2,
            club=club,
            role=None,
            is_admin=False,
            is_old=False,
        )

        self.client.force_authenticate(user=self.user_2)
        response = self.client.post(
            reverse("create_channel"),
            {
                "name": "club-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_2.id],
                "channel_of": str(club.id),
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_user_can_list_all_channels_and_request_join(self):
        self.client.force_authenticate(user=self.user_1)
        response = self.client.post(
            reverse("create_channel"),
            {
                "name": "public-room",
                "members": [self.user_1.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = response.data["channel_id"]

        self.client.force_authenticate(user=self.user_2)
        list_response = self.client.get(reverse("channels_list"), {"scope": "all"})
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data["channels"]), 1)
        self.assertFalse(list_response.data["channels"][0]["is_member"])
        self.assertTrue(list_response.data["channels"][0]["can_request_join"])

        join_response = self.client.post(
            reverse("channel_join_request_create", kwargs={"channel_id": channel_id}),
            {},
            format="json",
        )
        self.assertEqual(join_response.status_code, 201)
        self.assertTrue(
            ChannelJoinRequest.objects.filter(
                channel_id=channel_id,
                student=self.student_2,
                status=ChannelJoinRequest.Status.PENDING,
            ).exists()
        )

    def test_channel_admin_can_list_pending_join_requests(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "pending-room",
                "members": [self.user_1.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        self.client.force_authenticate(user=self.user_2)
        self.client.post(
            reverse("channel_join_request_create", kwargs={"channel_id": channel_id}),
            {},
            format="json",
        )

        self.client.force_authenticate(user=self.user_1)
        list_response = self.client.get(
            reverse("channel_join_requests_list", kwargs={"channel_id": channel_id})
        )
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data["requests"]), 1)
        self.assertEqual(
            list_response.data["requests"][0]["student_id"],
            self.user_2.id,
        )

    def test_non_admin_cannot_list_or_accept_join_requests(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "private-room",
                "members": [self.user_1.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        self.client.force_authenticate(user=self.user_2)
        self.client.post(
            reverse("channel_join_request_create", kwargs={"channel_id": channel_id}),
            {},
            format="json",
        )
        join_request = ChannelJoinRequest.objects.get(
            channel_id=channel_id,
            student=self.student_2,
        )

        self.client.force_authenticate(user=self.user_3)
        list_response = self.client.get(
            reverse("channel_join_requests_list", kwargs={"channel_id": channel_id})
        )
        self.assertEqual(list_response.status_code, 403)

        accept_response = self.client.post(
            reverse(
                "channel_join_request_accept",
                kwargs={"channel_id": channel_id, "join_request_id": join_request.id},
            ),
            {},
            format="json",
        )
        self.assertEqual(accept_response.status_code, 403)

    def test_channel_admin_can_accept_join_request(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "approval-room",
                "members": [self.user_1.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        self.client.force_authenticate(user=self.user_2)
        self.client.post(
            reverse("channel_join_request_create", kwargs={"channel_id": channel_id}),
            {},
            format="json",
        )
        join_request = ChannelJoinRequest.objects.get(
            channel_id=channel_id,
            student=self.student_2,
        )

        public_key = serialization.load_pem_public_key(
            self.student_2.public_key.encode("utf-8")
        )
        encrypted_key = public_key.encrypt(
            os.urandom(32),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        encrypted_key_b64 = base64.b64encode(encrypted_key).decode("utf-8")

        self.client.force_authenticate(user=self.user_1)
        accept_response = self.client.post(
            reverse(
                "channel_join_request_accept",
                kwargs={"channel_id": channel_id, "join_request_id": join_request.id},
            ),
            {"encrypted_key": encrypted_key_b64},
            format="json",
        )
        self.assertEqual(accept_response.status_code, 200)
        join_request.refresh_from_db()
        self.assertEqual(join_request.status, ChannelJoinRequest.Status.ACCEPTED)
        channel = Channel.objects.get(pk=channel_id)
        self.assertTrue(channel.members.filter(pk=self.student_2.pk).exists())
        self.assertTrue(channel.encrypted_keys.filter(student=self.student_2).exists())

    def test_channel_admin_can_add_member_without_join_request(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "direct-add-room",
                "members": [self.user_1.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        public_key_response = self.client.get(
            reverse("student_public_key_by_user", kwargs={"user_id": self.user_2.id})
        )
        self.assertEqual(public_key_response.status_code, 200)
        public_key = serialization.load_pem_public_key(
            public_key_response.data["public_key"].encode("utf-8")
        )
        encrypted_key = public_key.encrypt(
            os.urandom(32),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        encrypted_key_b64 = base64.b64encode(encrypted_key).decode("utf-8")

        add_member_response = self.client.post(
            reverse("channel_add_member", kwargs={"channel_id": channel_id}),
            {
                "student_user_id": self.user_2.id,
                "encrypted_key": encrypted_key_b64,
            },
            format="json",
        )
        self.assertEqual(add_member_response.status_code, 200)
        channel = Channel.objects.get(pk=channel_id)
        self.assertTrue(channel.members.filter(pk=self.student_2.pk).exists())
        self.assertTrue(
            channel.encrypted_keys.filter(student=self.student_2).exists()
        )

    def test_non_admin_cannot_add_member_without_join_request(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "forbidden-add-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        self.client.force_authenticate(user=self.user_2)
        add_member_response = self.client.post(
            reverse("channel_add_member", kwargs={"channel_id": channel_id}),
            {
                "student_user_id": self.user_3.id,
                "encrypted_key": "ZmFrZS1rZXk=",
            },
            format="json",
        )
        self.assertEqual(add_member_response.status_code, 403)

    def test_author_can_delete_own_message(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "delete-own-message-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        self.client.force_authenticate(user=self.user_2)
        create_message_response = self.client.post(
            reverse("create_message"),
            {
                "channel": channel_id,
                "by_club": "-1",
                "content": "message-to-delete",
            },
            format="json",
        )
        message_id = create_message_response.data["message_id"]

        delete_response = self.client.delete(
            reverse("delete_channel_message", kwargs={"message_id": message_id})
        )
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(Message.objects.filter(pk=message_id).exists())

    def test_channel_admin_can_delete_other_member_message(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "delete-admin-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        self.client.force_authenticate(user=self.user_2)
        create_message_response = self.client.post(
            reverse("create_message"),
            {
                "channel": channel_id,
                "by_club": "-1",
                "content": "member-message",
            },
            format="json",
        )
        message_id = create_message_response.data["message_id"]

        self.client.force_authenticate(user=self.user_1)
        delete_response = self.client.delete(
            reverse("delete_channel_message", kwargs={"message_id": message_id})
        )
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(Message.objects.filter(pk=message_id).exists())

    def test_non_author_non_admin_cannot_delete_message(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "delete-forbidden-room",
                "members": [self.user_1.id, self.user_2.id, self.user_3.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        self.client.force_authenticate(user=self.user_2)
        create_message_response = self.client.post(
            reverse("create_message"),
            {
                "channel": channel_id,
                "by_club": "-1",
                "content": "protected-message",
            },
            format="json",
        )
        message_id = create_message_response.data["message_id"]

        self.client.force_authenticate(user=self.user_3)
        delete_response = self.client.delete(
            reverse("delete_channel_message", kwargs={"message_id": message_id})
        )
        self.assertEqual(delete_response.status_code, 403)
        self.assertTrue(Message.objects.filter(pk=message_id).exists())

    def test_channel_admin_can_delete_all_messages(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "purge-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        self.client.force_authenticate(user=self.user_1)
        self.client.post(
            reverse("create_message"),
            {"channel": channel_id, "by_club": "-1", "content": "admin-message"},
            format="json",
        )
        self.client.force_authenticate(user=self.user_2)
        self.client.post(
            reverse("create_message"),
            {"channel": channel_id, "by_club": "-1", "content": "member-message"},
            format="json",
        )

        self.client.force_authenticate(user=self.user_1)
        purge_response = self.client.delete(
            reverse("delete_all_channel_messages", kwargs={"channel_id": channel_id})
        )
        self.assertEqual(purge_response.status_code, 200)
        self.assertEqual(Message.objects.filter(channel_id=channel_id).count(), 0)

    def test_channel_admin_can_delete_channel(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "delete-channel-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        self.client.post(
            reverse("create_message"),
            {"channel": channel_id, "by_club": "-1", "content": "to-be-deleted"},
            format="json",
        )

        delete_channel_response = self.client.delete(
            reverse("delete_channel", kwargs={"channel_id": channel_id})
        )
        self.assertEqual(delete_channel_response.status_code, 200)
        self.assertFalse(Channel.objects.filter(pk=channel_id).exists())
        self.assertEqual(Message.objects.filter(channel_id=channel_id).count(), 0)

    def test_non_admin_cannot_delete_all_messages(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "purge-forbidden-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        self.client.force_authenticate(user=self.user_2)
        purge_response = self.client.delete(
            reverse("delete_all_channel_messages", kwargs={"channel_id": channel_id})
        )
        self.assertEqual(purge_response.status_code, 403)

    def test_non_admin_cannot_delete_channel(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "delete-channel-forbidden-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        self.client.force_authenticate(user=self.user_2)
        delete_channel_response = self.client.delete(
            reverse("delete_channel", kwargs={"channel_id": channel_id})
        )
        self.assertEqual(delete_channel_response.status_code, 403)
        self.assertTrue(Channel.objects.filter(pk=channel_id).exists())

    def test_channel_admin_can_list_members(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "members-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        list_response = self.client.get(
            reverse("channel_members_list", kwargs={"channel_id": channel_id})
        )
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data["members"]), 2)
        self.assertTrue(
            any(member["user_id"] == self.user_1.id for member in list_response.data["members"])
        )
        self.assertTrue(
            any(member["user_id"] == self.user_2.id for member in list_response.data["members"])
        )

    def test_non_admin_cannot_list_members(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "members-forbidden-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        self.client.force_authenticate(user=self.user_2)
        list_response = self.client.get(
            reverse("channel_members_list", kwargs={"channel_id": channel_id})
        )
        self.assertEqual(list_response.status_code, 403)

    def test_channel_admin_can_remove_member(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "remove-member-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        remove_response = self.client.delete(
            reverse(
                "channel_remove_member",
                kwargs={"channel_id": channel_id, "user_id": self.user_2.id},
            )
        )
        self.assertEqual(remove_response.status_code, 200)
        channel = Channel.objects.get(pk=channel_id)
        self.assertFalse(channel.members.filter(pk=self.student_2.pk).exists())
        self.assertFalse(channel.admins.filter(pk=self.student_2.pk).exists())
        self.assertFalse(channel.encrypted_keys.filter(student=self.student_2).exists())

    def test_non_admin_cannot_remove_member(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "remove-member-forbidden-room",
                "members": [self.user_1.id, self.user_2.id, self.user_3.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        self.client.force_authenticate(user=self.user_2)
        remove_response = self.client.delete(
            reverse(
                "channel_remove_member",
                kwargs={"channel_id": channel_id, "user_id": self.user_3.id},
            )
        )
        self.assertEqual(remove_response.status_code, 403)
        channel = Channel.objects.get(pk=channel_id)
        self.assertTrue(channel.members.filter(pk=self.student_3.pk).exists())

    def test_member_can_leave_channel(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "leave-room",
                "members": [self.user_1.id, self.user_2.id],
                "admins": [self.user_1.id, self.user_2.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        self.client.force_authenticate(user=self.user_2)
        leave_response = self.client.post(
            reverse("channel_leave", kwargs={"channel_id": channel_id}),
            {},
            format="json",
        )
        self.assertEqual(leave_response.status_code, 200)

        channel = Channel.objects.get(pk=channel_id)
        self.assertFalse(channel.members.filter(pk=self.student_2.pk).exists())
        self.assertFalse(channel.admins.filter(pk=self.student_2.pk).exists())
        self.assertFalse(channel.encrypted_keys.filter(student=self.student_2).exists())

    def test_non_member_cannot_leave_channel(self):
        self.client.force_authenticate(user=self.user_1)
        create_channel_response = self.client.post(
            reverse("create_channel"),
            {
                "name": "leave-forbidden-room",
                "members": [self.user_1.id],
                "admins": [self.user_1.id],
                "channel_of": "-1",
            },
            format="json",
        )
        channel_id = create_channel_response.data["channel_id"]

        self.client.force_authenticate(user=self.user_2)
        leave_response = self.client.post(
            reverse("channel_leave", kwargs={"channel_id": channel_id}),
            {},
            format="json",
        )
        self.assertEqual(leave_response.status_code, 400)
