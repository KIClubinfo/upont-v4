import csv
import io

from django.contrib.auth import models as models
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from social.models import Promotion, Student


@login_required()
def add(request):
    order = "promo, nom, prénom, mail"
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("login"))
    context = {
        "order": order,
    }
    if request.method == "GET":
        return render(request, "add_promo.html", context)

    if "file" in request.FILES:
        csv_file = request.FILES["file"]
    else:
        context = {
            "order": order,
            "no_file": True,
            "promo_not_added": True,
        }
        return render(request, "add_promo.html", context)

    if not csv_file.name.endswith(".csv"):
        context = {
            "order": order,
            "type_error": True,
            "promo_not_added": True,
        }
        return render(request, "add_promo.html", context)
    data_set = csv_file.read().decode("UTF-8")
    io_string = io.StringIO(data_set)
    next(io_string)
    students_not_added = []
    for column in csv.reader(io_string, delimiter=";", quotechar="|"):
        password = models.User.objects.make_random_password()  # à envoyer par mail
        user, created = models.User.objects.update_or_create(
            last_name=column[1],
            first_name=column[2],
            username=column[1] + "." + column[2],
            email=column[3],
        )
        if created:
            user.set_password(password)
        student, created2 = Student.objects.update_or_create(
            user=user,
            promo=Promotion.objects.get(year=column[0]),
            department=Student.Department.A1,
        )
        if not created or not created2:
            students_not_added.append(column[1] + "." + column[2])
    context = {
        "order": order,
        "promo_added": True,
        "students_not_added": students_not_added,
    }
    return render(request, "add_promo.html", context)
