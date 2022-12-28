from unittest.mock import MagicMock

from django.contrib.auth import models
from django.core.files import File
from django.test import TestCase
from django.utils import timezone
from news.models import Post
from social.models import Student

from .models import Resources


class ResourcesModelTest(TestCase):
    def test_ressource_saves_in_database(self):
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

        resources = Resources(
            name="Name",
            author=student,
            date=timezone.now(),
            post=post,
            file=file_mock,
        )
        resources.save()

        retrieved_resources = Resources.objects.get(pk=resources.pk)

        self.assertEqual(retrieved_resources, resources)
