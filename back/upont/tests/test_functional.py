from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from selenium import webdriver


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


# class MySeleniumTests(StaticLiveServerTestCase):
#     @classmethod
#     def setUpClass(cls):
#         # super().setUpClass()
#         # cls.selenium = webdriver.Chrome
#         cls.driver = webdriver.Chrome()
#
#     @classmethod
#     def tearDownClass(cls):
#         # cls.selenium.quit()
#         # super().tearDownClass()
#         cls.driver.quit
#
#     def test_login(self):
#         # self.selenium.get('%s%s' % (self.live_server_url, '/login/'))
#         # username_input = self.selenium.find_element_by_name("username")
#         # username_input.send_keys('test@mail.com')
#         # password_input = self.selenium.find_element_by_name("password")
#         # password_input.send_keys('NotSecret')
#         # self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()
#          cls.driver


class MySeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):

        cls.driver = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_login(self):
        self.driver.get("http://selenium.dev")
