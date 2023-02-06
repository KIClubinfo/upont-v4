import csv
import io

from django.contrib.auth import models as models
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from social.models import Promotion, Student

from .settings import LOGIN_REDIRECT_URL, LOGIN_URL

@login_required
def add(request):
    order = "name, teachers, department, acronym"
    if not request.user.is_superuser:
        raise PermissionDenied()
    context = {
        "order": order,
    }
    if request.method == "GET":
        return render(request, "add_courses.html", context)

    if "file" in request.FILES:
        csv_file = request.FILES["file"]
    else:
        context = {
            "order": order,
            "no_file": True,
            "courses_not_added": True,
        }
        return render(request, "add_promo.html", context)

    if not csv_file.name.endswith(".csv"):
        context = {
            "order": order,
            "type_error": True,
            "courses_not_added": True,
        }
        return render(request, "add_courses.html", context)
    data_set = csv_file.read().decode("UTF-8")
    io_string = io.StringIO(data_set)
    next(io_string)
    courses_not_added = []
    for column in csv.reader(io_string, delimiter="\t", quotechar="|"):
        Course, created = models.User.objects.get_or_create(
        name=column[1],
        teachers=map(lambda teacher: teacher.strip(), column[2].split(","))
        department=column[3],
        acronym=column[3],
        )
        if  (name="") or (teachers="") or (department="") or (acronym=""):
            courses_not_added.append(column),
        if not department in models.CourseDepartment.values:
            department=="AHE"
            
        courses, created3 = teacher.objects.get_or_create(
            name=teachers,
        )   
        if not created:
            courses_not_added.append(
                (column)
            )
            context = {
                "order": order,
                "type_error": True,
                "courses_not_added": courses_not_added,
    }
    return render(request, "add_courses.html", context)