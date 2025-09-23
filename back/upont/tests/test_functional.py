from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from ..settings import LOGIN_REDIRECT_URL


class TestAuthenticate(TestCase):
    def check_wrong_form_triggers_errors(self, named_url, context):
        response = self.client.post(reverse(named_url), context)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context[1].get("form").errors)
        return response

    def generate_token(self):
        response = self.client.post(
            reverse("password_reset"), {"email": self.user.email}
        )
        token = response.context[0]["token"]
        uid = response.context[0]["uid"]
        return uid, token

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

    def test_login_with_correct_username_and_password_authenticates_and_redirects(
            self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": self.password},
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse(LOGIN_REDIRECT_URL))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_correct_email_and_password_authenticates_and_redirects(
            self):
        response = self.client.post(
            reverse("login"), {
                "username": self.user.email, "password": self.password})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse(LOGIN_REDIRECT_URL))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_wrong_password_fails(self):
        response = self.check_wrong_form_triggers_errors(
            "login", {"username": self.user.username, "password": "wrong_password"}
        )
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_with_wrong_username_fails(self):
        response = self.check_wrong_form_triggers_errors(
            "login", {"username": "wrong_username", "password": self.password}
        )
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_redirects_to_login_page_when_acessing_a_page_without_login(self):
        requested_url = reverse("social:index_users")
        response = self.client.get(requested_url)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(
            response.url,
            reverse("login") +
            "?next=" +
            reverse("social:index_users"))

    def test_getting_logout_page_logs_out(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse("login"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.client.get(reverse("logout"))
        response = self.client.get(reverse("login"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_password_reset_form_with_wrongly_shaped_mail_fails(self):
        self.check_wrong_form_triggers_errors(
            "password_reset", {"email": "wrong.email"}
        )

    def test_password_reset_form_with_unknown_mail_fails_silently(self):
        response = self.client.post(
            reverse("password_reset"), {"email": "whosthatguy@mail.com"}
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_form_redirects_and_sends_mail_with_token(self):
        response = self.client.post(
            reverse("password_reset"), {"email": self.user.email}
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        self.assertEqual(
            sent_mail.subject, "[uPont] Demande de changement de mot de passe"
        )
        token = response.context[0]["token"]
        self.assertIn(token, sent_mail.body)

    def test_getting_password_reset_confirm_with_wrong_token_prints_message(
            self):
        response = self.client.get(
            reverse(
                "password_reset_confirm",
                kwargs={
                    "uidb64": "foo",
                    "token": "bar"}))
        self.assertEquals(response.status_code, 200)
        self.assertIn(b"plus valide", response.content)

    def test_getting_password_reset_confirm_with_wrong_token_displays_form(
            self):
        uid, token = self.generate_token()
        response = self.client.get(
            reverse(
                "password_reset_confirm",
                kwargs={
                    "uidb64": uid,
                    "token": token}),
            follow=True,
        )
        self.assertEquals(response.status_code, 200)
        self.assertIn(b"Rentre ton nouveau mot de passe", response.content)

    def test_password_reset_resets_password_and_redirects(self):
        uid, token = self.generate_token()
        response = self.client.get(
            reverse(
                "password_reset_confirm",
                kwargs={
                    "uidb64": uid,
                    "token": token}))
        response = self.client.post(
            response.url,
            {"new_password1": "new_password", "new_password2": "new_password"},
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse("password_reset_complete"))
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": "new_password"},
        )
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_password_change_changes_password_and_redirects(self):
        self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": self.password},
        )
        response = self.client.post(
            reverse("password_change"),
            {
                "old_password": self.password,
                "new_password1": "new_password",
                "new_password2": "new_password",
            },
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse("password_change_done"))
        response = self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": "new_password"},
        )
        self.assertTrue(response.wsgi_request.user.is_authenticated)
