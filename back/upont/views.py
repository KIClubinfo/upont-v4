from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, "index.html")


def index_admin(request):
    return render(request, "index_admin.html")


def index_users(request):
    return render(request, "index_users.html")


def index_profil(request):
    return render(request, "index_profil.html")
