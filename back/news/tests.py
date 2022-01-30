import datetime

from django.contrib.auth import models
from django.http import HttpRequest
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from social.models import Club, Membership, Student

from .models import Comment, Participation, Post, Shotgun
from .views import posts


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


class CommentModelTest(TestCase):
    def test_comment_saves_in_database(self):
        post_user = models.User(username="post_user")
        post_user.save()
        post_author = Student(
            user=post_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        post_author.save()
        post = Post(
            title="Test Post",
            author=post_author,
            date=timezone.now() - datetime.timedelta(days=1),
            content="Some test post",
        )
        post.save()
        comment_user = models.User(username="comment_user")
        comment_user.save()
        comment_author = Student(
            user=comment_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        comment_author.save()
        comment = Comment(
            post=post,
            author=comment_author,
            date=timezone.now(),
            content="Some test comment",
        )
        comment.save()
        retrieved_comment = Comment.objects.get(pk=comment.pk)
        self.assertEqual(retrieved_comment.pk, comment.pk)


class CommentViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        post_user = models.User(username="post_user")
        post_user.save()
        post_author = Student(
            user=post_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        post_author.save()
        cls.post = Post(
            title="Test Post",
            author=post_author,
            date=timezone.now() - datetime.timedelta(days=1),
            content="Some test post",
        )
        cls.post.save()
        cls.comment_user = models.User(username="comment_user")
        cls.comment_user.save()
        cls.comment_author = Student(
            user=cls.comment_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        cls.comment_author.save()
        cls.club = Club(
            name="Test Club",
            description="Some test club",
            active=True,
            has_fee=False,
        )
        cls.club.save()
        comment_author_club_membership = Membership(
            is_admin=False,
            club=cls.club,
            student=cls.comment_author,
        )
        comment_author_club_membership.save()

    def create_comment_from_student(self):
        comment = Comment(
            post=self.post,
            author=self.comment_author,
            date=timezone.now(),
            content="Some test comment",
        )
        comment.save()
        return comment

    def create_comment_from_club(self):
        comment = Comment(
            post=self.post,
            author=self.comment_author,
            club=self.club,
            date=timezone.now(),
            content="Some test comment",
        )
        comment.save()
        return comment

    def test_sending_comment_on_post_creates_comment(self):
        comment_request = HttpRequest()
        comment_request.method = "POST"
        comment_request.POST = {
            "post": self.post.pk,
            "club": "",
            "content": "Some test comment from a student",
        }
        comment_request.user = self.comment_user
        response = posts(comment_request)
        self.assertEqual(response.status_code, 302)
        retrieved_comment = Comment.objects.get(post=self.post)
        self.assertEqual(retrieved_comment.content, comment_request.POST["content"])

    def test_deleting_my_own_comment_on_post_works(self):
        # Create several comments to check whether the view actually deletes only one comment
        self.create_comment_from_student()
        comment = self.create_comment_from_student()
        client = Client()
        client.force_login(self.comment_user)
        response = client.get(
            reverse("news:comment_delete", args=(comment.id, self.post.id))
        )
        self.assertEqual(response.status_code, 302)
        retrieved_comments = Comment.objects.filter(post=self.post)
        self.assertEqual(len(retrieved_comments), 1)

    def test_deleting_someone_else_comment_fails(self):
        self.create_comment_from_student()
        comment = self.create_comment_from_student()
        deleter_user = models.User(username="deleter_user")
        deleter_user.save()
        deleter_student = Student(
            user=deleter_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        deleter_student.save()
        client = Client()
        client.force_login(deleter_user)
        response = client.get(
            reverse("news:comment_delete", args=(comment.id, self.post.id))
        )
        self.assertEqual(response.status_code, 302)
        retrieved_comments = Comment.objects.filter(post=self.post)
        self.assertEqual(len(retrieved_comments), 2)

    def test_sending_comment_on_post_as_club_creates_comment(self):
        comment_request = HttpRequest()
        comment_request.method = "POST"
        comment_request.POST = {
            "post": self.post.pk,
            "club": self.club,
            "content": "Some test comment from a club",
        }
        comment_request.user = self.comment_user
        response = posts(comment_request)
        self.assertEqual(response.status_code, 302)
        retrieved_comment = Comment.objects.get(post=self.post)
        self.assertEqual(retrieved_comment.content, comment_request.POST["content"])

    def test_deleting_post_from_another_club_fails(self):
        self.create_comment_from_club()
        comment = self.create_comment_from_club()
        deleter_user = models.User(username="deleter_user")
        deleter_user.save()
        deleter_student = Student(
            user=deleter_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        deleter_student.save()
        deleter_club_membership = Membership(
            is_admin=False,
            club=self.club,
            student=deleter_student,
        )
        deleter_club_membership.save()
        client = Client()
        client.force_login(deleter_user)
        response = client.get(
            reverse("news:comment_delete", args=(comment.id, self.post.id))
        )
        self.assertEqual(response.status_code, 302)
        retrieved_comments = Comment.objects.filter(post=self.post)
        self.assertEqual(len(retrieved_comments), 1)

    def test_deleting_post_from_someone_else_in_my_club_works(self):
        self.create_comment_from_club()
        comment = self.create_comment_from_club()
        deleter_user = models.User(username="deleter_user")
        deleter_user.save()
        deleter_student = Student(
            user=deleter_user,
            department=Student.Department.A1,
            gender=Student.Gender.A,
            origin=Student.Origin.CC,
            phone_number="+33666666666",
        )
        deleter_student.save()
        other_club = Club(
            name="Other Test Club",
            description="Some other test club",
            active=True,
            has_fee=False,
        )
        other_club.save()
        deleter_club_membership = Membership(
            is_admin=False,
            club=other_club,
            student=deleter_student,
        )
        deleter_club_membership.save()
        client = Client()
        client.force_login(deleter_user)
        response = client.get(
            reverse("news:comment_delete", args=(comment.id, self.post.id))
        )
        self.assertEqual(response.status_code, 302)
        retrieved_comments = Comment.objects.filter(post=self.post)
        self.assertEqual(len(retrieved_comments), 2)
