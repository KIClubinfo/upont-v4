"""upont URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='login.html', extra_context={'next':""}),
        name="login"
    ),
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(template_name='password_change.html'),
        name="password_change"
    ),
    path(
        'password_change_done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
        name="password_change_done"
    ),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html',
            email_template_name="password_reset_email.html",
            subject_template_name="password_reset_subject.txt",
            success_url="password_reset_done"
        ),
        name="password_reset"
    ),
    path(
        'password_reset_done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='password_reset_done.html'),
        name="password_reset_done"
    ),
   path(
        'password_reset_confirm/',
        auth_views.PasswordResetView.as_view(template_name='password_reset_confirm.html', success_url="password_reset_complete"),
        name="password_reset_confirm"
    ),
    path(
        'password_reset_complete/',
        auth_views.PasswordResetView.as_view(template_name='password_reset_complete.html'),
        name="password_reset_complete"
    ),
    path("", views.index),
    path("index_admin/", views.index_admin),
    path("index_users/", views.index_users),
    path("index_profil/", views.index_profil),
    path("admin/", admin.site.urls),
]
