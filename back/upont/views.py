from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import views as auth_views


def index(request):
    return render(request, "index.html")


def index_admin(request):
    return render(request, "index_admin.html")


def index_users(request):
    return render(request, "index_users.html")


def index_profil(request):
    return render(request, "index_profil.html")


class Login(auth_views.LoginView):
    template_name = 'login.html'
    extra_context = {'next': "/"}


class PasswordChange(auth_views.PasswordChangeView):
    template_name = 'password_change.html'


class PasswordChangeDone(auth_views.PasswordChangeDoneView):
    template_name = 'password_change_done.html'


class PasswordReset(auth_views.PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = "password_reset_email.html"
    subject_template_name = "password_reset_subject.txt"
    success_url = "password_reset_done"


class PasswordResetDone(auth_views.PasswordResetDoneView):
    template_name = 'password_reset_done.html'


class PasswordResetConfirm(auth_views.PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = "password_reset_complete"


class PasswordResetComplete(auth_views.PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'
