import csv
import io
import logging
import mimetypes
import os
from urllib.parse import unquote

from django.conf import settings
from django.contrib.auth import get_user_model
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
from django_cas_ng.signals import cas_user_authenticated
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from social.models import Promotion, Student
from upont.auth import EmailBackend

from .settings import LOGIN_REDIRECT_URL, LOGIN_URL

logger = logging.getLogger(__name__)


User = get_user_model()


def root_redirect(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse(LOGIN_REDIRECT_URL))
    else:
        return HttpResponseRedirect(reverse(LOGIN_URL))


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def auth_check(request):
    print(f"DEBUG: Token auth successful for user: {request.user}")
    return HttpResponse(status=200)


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
        username = column[2].lower() + "." + column[1].lower()
        user, created = models.User.objects.get_or_create(
            last_name=column[1].capitalize(),
            first_name=column[2].capitalize(),
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


@api_view(["GET"])
@permission_classes([AllowAny])
def get_sso_token(request):
    """
    Authentifie un utilisateur via SSO CAS et retourne un token d'authentification Django.
    Redirige l'utilisateur vers l'application mobile avec le token.
    """
    ticket = request.GET.get("ticket")
    service = request.build_absolute_uri(request.path)
    service = service.replace("http://", "https://")

    if not ticket:
        return Response({"error": "Ticket CAS manquant"}, status=400)

    created_flag = {"value": False}  # Use a mutable object to capture changes

    # Define a simple inline signal handler and authenticate the user
    def user_authenticated_handler(sender, user, created, **kwargs):
        if created:
            created_flag["value"] = True

    cas_user_authenticated.connect(user_authenticated_handler, weak=False)
    user = CASBackend().authenticate(request, ticket=ticket, service=service)
    cas_user_authenticated.disconnect(user_authenticated_handler)
    logger.info("=== DEBUG USER ===")
    logger.info(f"Username: {user.username}")
    logger.info(f"First name: {user.first_name}")
    logger.info(f"Last name: {user.last_name}")
    logger.info(f"Email: {user.email}")
    logger.info(f"ID: {user.id}")
    logger.info(f"Is active: {user.is_active}")
    logger.info(f"Is staff: {user.is_staff}")
    logger.info(f"Is superuser: {user.is_superuser}")
    logger.info(f"Date joined: {user.date_joined}")
    logger.info(f"Last login: {user.last_login}")
    # Pour voir tous les champs du mod  le, utile pour debug
    logger.info(f"All fields: {user.__dict__}")

    if not user:
        return Response({"error": "Échec de l'authentification CAS"}, status=403)

    def capitalize_name_parts(name_str):
        if not name_str:
            return ""
        parts = name_str.split("-")
        capitalized_parts = [part.capitalize() for part in parts if part]
        return "-".join(capitalized_parts)

    User = get_user_model()

    first_name, last_name = (
        user.username.split(".", 1) if "." in user.username else (user.username, "")
    )
    first_name = capitalize_name_parts(first_name)
    last_name = capitalize_name_parts(last_name)

    # 1️⃣ Vérifier si le username CAS existe
    try:
        user_check = User.objects.get(username=user.username)
    except User.DoesNotExist:
        user_check = None

    # 2️⃣ Sinon, chercher un user avec même prénom et nom
    if not user_check:
        try:
            user_check = User.objects.get(first_name=first_name, last_name=last_name)
        except User.DoesNotExist:
            user_check = None

    # 3️⃣ Si aucun user trouvé, créer un nouvel utilisateur
    if not user_check:
        base_username = user.username
        counter = 1
        while User.objects.filter(username=base_username).exists():
            base_username = f"{user.username}{counter}"
            counter += 1

        user_check = User.objects.create_user(
            username=base_username,
            email=f"{base_username}@eleves.enpc.fr",
            first_name=first_name,
            last_name=last_name,
        )
    student, created2 = Student.objects.get_or_create(
        user=user_check,
    )
    if created2:
        student.promo = Promotion.objects.order_by("-nickname").first()
        student.is_validated = False
        student.save()

    if created_flag["value"]:

        if created2:
            student.is_validated = False
            student.save()

    token, _ = Token.objects.get_or_create(user=user_check)

    redirect_url = f"upont://login?token={token.key}"

    return HttpResponse(
        f"""
        <html>
        <head>
            <meta http-equiv="refresh" content="0;url={redirect_url}">
        </head>
        <body>
            <p>Si vous n'êtes pas redirigé, <a href="{redirect_url}">cliquez ici</a>.</p>
        </body>
        </html>
        """
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_admin_status(request):
    """
    Returns the admin status of the currently authenticated user.
    Includes superuser and staff status information.
    """
    user = request.user
    status = {
        "is_superuser": user.is_superuser,
        "is_staff": user.is_staff,
    }
    return Response(status)


class AdminStatusViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Returns the admin status of the currently authenticated user.
        Includes superuser and staff status information.
        """
        user = request.user
        status = {
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
        }
        return Response(status)


def privacy(request):
    return render(request, "privacy.html")


def contact(request):
    return render(request, "contact.html")
