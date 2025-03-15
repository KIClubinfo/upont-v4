import csv
import io
import mimetypes
import os
from urllib.parse import unquote

from django.conf import settings
from django.contrib.auth import models as models
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import (
    FileResponse,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.urls import reverse
from django_cas_ng.backends import CASBackend
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from social.models import Promotion, Student
from upont.auth import EmailBackend

from .settings import LOGIN_REDIRECT_URL, LOGIN_URL


def root_redirect(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse(LOGIN_REDIRECT_URL))
    else:
        return HttpResponseRedirect(reverse(LOGIN_URL))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_media_path(request, path):
    """
    The get_media_path function is a helper function that takes in the request and
    path of a file. It then checks if the file exists, and returns an error message if
    it does not exist. If it does exist, it will return an HttpResponse with the
    correct headers to serve up the media.

    @param request: Get the user's authentication token
    @param path: Determine the path of the file to be served
    return: A FileResponse object that contains the file specified in the path parameter
    """
    if not os.path.exists(f"{settings.MEDIA_ROOT}/{path}"):
        return Response(
            {"status": "error", "message": "No such file exists."}, status=404
        )
    # retrieve user authentication token from cookies
    # I'm using django-rest-framework token authentication

    if request.user is not None:
        # Guess the MIME type of a file. Like pdf/docx/xlsx/png/jpeg
        mimetype, encoding = mimetypes.guess_type(path, strict=True)
        if not mimetype:
            mimetype = "text/html"
        # By default, percent-encoded sequences are decoded with UTF-8, and invalid
        # sequences are replaced by a placeholder character.
        # Example: unquote('abc%20def') -> 'abc def'.
        file_path = unquote(os.path.join(settings.MEDIA_ROOT, path)).encode("utf-8")
        # FileResponse - A streaming HTTP response class optimized for files.
        return FileResponse(open(file_path, "rb"), content_type=mimetype)
    return Response("Access to this file is permitted.", status=404)


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
        debut = column[3].split("@")[0]
        if len(debut.split(".")[1].split("-")) > 1:
            username = debut.split(".")[0][0] + "." + debut.split(".")[1]
        else:
            username = debut
        user, created = models.User.objects.get_or_create(
            last_name=column[1],
            first_name=column[2],
            username=username,
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


@api_view(["POST"])
@permission_classes([AllowAny])
def get_token(request):
    if "email" not in request.data or "password" not in request.data:
        return Response({"error": "Please provide both email and password"})
    user = EmailBackend().authenticate(
        request, username=request.data["email"], password=request.data["password"]
    )
    if user is None:
        return Response({"error": "Invalid credentials"})
    token, created = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})


@api_view(["POST"])
@permission_classes([AllowAny])
def get_sso_token(request):
    """
    Permet de récupérer un token d'authentification via SSO.
    La requête doit contenir un paramètre 'ticket' (ticket CAS obtenu après authentification).
    """
    ticket = request.data.get("ticket")
    if not ticket:
        return Response({"error": "Le ticket CAS est requis."}, status=400)

    service = request.data.get("service", settings.CAS_REDIRECT_URL)

    user = CASBackend().authenticate(request, ticket=ticket, service=service)
    if user is None:
        return Response(
            {"error": "Ticket CAS invalide ou authentification échouée."}, status=400
        )

    token, created = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})


def privacy(request):
    return render(request, "privacy.html")


def contact(request):
    return render(request, "contact.html")
