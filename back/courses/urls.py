import csv
import io

from django.contrib.auth import models as models
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from course.models import Course, Teacher

from .settings import LOGIN_REDIRECT_URL, LOGIN_URL


app_name = "course"


urlpatterns = [
    path("add_course/", views.add, name="add_course"),
]
