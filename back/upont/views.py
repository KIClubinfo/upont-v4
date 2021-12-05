from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from django.shortcuts import render


def login(request):
    return render(request, "login.html")