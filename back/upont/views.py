from django.http import HttpResponse
from django.shortcuts import render


def glasscard(request):
    return render(request, "GlassCard.html")

def index_users(request):
    return render(request, "index_users.html")

def index_profil(request):
    return render(request, "index_profil.html")
