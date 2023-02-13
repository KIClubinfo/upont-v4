import django_cas_ng.views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django_reverse_js.views import urls_js
from rest_framework import routers
from . import views



app_name = "course"


urlpatterns = [
    path("add_course/", views.add, name="add_course"),
]
