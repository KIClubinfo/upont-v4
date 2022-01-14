from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import *
from django.test import SimpleTestCase
from django.urls import resolve, reverse


class TestUrls(SimpleTestCase):
    def test_login_url_resolves(self):
        url = reverse("login")
        self.assertEquals(resolve(url).func.view_class, LoginView)

    def test_logout_url_resolves(self):
        url = reverse("logout")
        self.assertEquals(resolve(url).func.view_class, LogoutView)

    def test_password_change_url_resolves(self):
        url = reverse("password_change")
        self.assertEquals(resolve(url).func.view_class, PasswordChangeView)

    def test_password_change_done_url_resolves(self):
        url = reverse("password_change_done")
        self.assertEquals(resolve(url).func.view_class, PasswordChangeDoneView)

    def test_password_reset_url_resolves(self):
        url = reverse("password_reset")
        self.assertEquals(resolve(url).func.view_class, PasswordResetView)

    def test_password_reset_done_url_resolves(self):
        url = reverse("password_reset_done")
        self.assertEquals(resolve(url).func.view_class, PasswordResetDoneView)

    def test_password_reset_confirm_url_resolves(self):
        url = reverse(
            "password_reset_confirm",
            kwargs={"uidb64": "Mg", "token": "ayd1gp-435793523dbd8f1e69f37053c440"},
        )
        self.assertEquals(resolve(url).func.view_class, PasswordResetConfirmView)

    def test_password_reset_complete_url_resolves(self):
        url = reverse("password_reset_complete")
        self.assertEquals(resolve(url).func.view_class, PasswordResetCompleteView)
