import csv
import io

from django.contrib.auth import models as models
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from . import models

from upont.settings import LOGIN_REDIRECT_URL, LOGIN_URL

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
    list_courses=[]
    list_teachers=[]
    for column in csv.reader(io_string, delimiter="\t", quotechar="|"):
        name=column[1],
        teachers=map(lambda teacher: teacher.strip(), column[2].split(","))
        department=column[3],
        acronym=column[3],
        if  (name=="") or (teachers=="") or (department=="") or (acronym==""):
            courses_not_added.append(column),
        if not department in models.CourseDepartment.values:
            department=="AHE"
        
        if (name not in list_courses):
            course, created = models.User.objects.get_or_create(
                name=name,
                department=department,
                acronym=acronym,
                teacher=teachers,
            )

            created.save()
            list_courses.append(name)

        if created:
            for i in range (len(teachers)):
                if teachers[i] not in list_teachers:
                    teacher, created2 = models.Teacher.objects.get_or_creat(
                        name=name
                    )
                    created2.save()
                    list_teachers.append(teachers[i])

        
        if not created:
            courses_not_added.append(
                (",".join(column))
            )
        context = {
            "order": order,
            "type_error": True,
            "courses_not_added": courses_not_added,
        }
    return render(request, "add_courses.html", context)