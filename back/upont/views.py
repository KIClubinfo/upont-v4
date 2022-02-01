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


def root_redirect(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse(LOGIN_REDIRECT_URL))
    else:
        return HttpResponseRedirect(reverse(LOGIN_URL))


def media(request, path):
    """
    When trying to access /media/path this function makes sures the user is authenticated.
    If it is the case then the media is served by the nginx server.
    Otherwise an http access error code is sent back.
    """
    access_granted = False
    user = request.user
    if user.is_authenticated:
        access_granted = True

    if access_granted:
        response = HttpResponse()
        # Content-type will be detected by nginx
        del response["Content-Type"]
        response["X-Accel-Redirect"] = "/protected/media/" + path
        return response
    else:
        return HttpResponseForbidden()


@login_required
def page_not_created(request):
    return render(request, "page_not_created.html")


@login_required
def add(request):
    order = "promo, nom, prénom, mail"
    if not request.user.is_superuser:
        raise PermissionDenied()
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
        user, created = models.User.objects.get_or_create(
            last_name=column[1],
            first_name=column[2],
            username=(column[2] + "." + column[1]).replace(" ", "-").lower(),
            email=column[3],
        )
        if created:
            user.set_password(password)
            user.save()
        promo, created3 = Promotion.objects.get_or_create(
            year=column[0], nickname="0" + str(column[0])
        )
        student, created2 = Student.objects.get_or_create(
            user=user,
        )
        if created2:
            student.department = Student.Department.A1
            student.promo = promo
            student.save()
        if not created or not created2:
            students_not_added.append(
                (column[2] + "." + column[1]).replace(" ", "-").lower()
            )
    context = {
        "order": order,
        "promo_added": True,
        "students_not_added": students_not_added,
    }
    return render(request, "add_promo.html", context)
