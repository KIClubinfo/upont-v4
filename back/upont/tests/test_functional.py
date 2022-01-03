from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from selenium.webdriver.chrome.webdriver import WebDriver


class LoginTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "password"
        cls.user = User.objects.create_user(
            username="john",
            email="john.doe@mail.com",
            password=cls.password,
            first_name="John",
            last_name="Doe",
        )

    def test_login_with_correct_credentials_authenticates_and_redirects(self):
        response = self.client.post(
            "/login/", {"username": self.user.username, "password": self.password}
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/social/index_users")
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_wrong_password_fails(self):
        response = self.client.post(
            "/login/", {"username": self.user.username, "password": "wrong_password"}
        )
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context[1].get("form").errors)
        self.assertTrue(not response.wsgi_request.user.is_authenticated)
