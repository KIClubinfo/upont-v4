from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import views as auth_views


def login(request):
    return render(request, "login.html")
