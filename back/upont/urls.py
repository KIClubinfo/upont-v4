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
    path("", views.index, name="index"),
    path("index_admin/", views.index_admin, name="index_admin"),
    path("index_users/", views.index_users, name="index_users"),
    path("index_profil/", views.index_profil, name="index_profil"),
    path("admin/", admin.site.urls),
    path('login/', views.Login.as_view(), name="login"),
    path('password_change/', views.PasswordChange.as_view(), name="password_change"),
    path('password_change_done/', views.PasswordChangeDone.as_view(), name="password_change_done"),
    path('password_reset/', views.PasswordReset.as_view(), name="password_reset"),
    path('password_reset_done/', views.PasswordResetDone.as_view(), name="password_reset_done"),
    path('password_reset_confirm/', views.PasswordResetConfirm.as_view(), name="password_reset_confirm"),
    path('password_reset_complete/', views.PasswordResetComplete.as_view(), name="password_reset_complete"),
]
