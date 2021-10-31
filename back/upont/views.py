from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, "index.html")

def proposition_1(request):
    return render(request, "index1.html")

def proposition_2(request):
    return render(request, "index2.html")