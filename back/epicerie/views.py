from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the epicerie index.")

def basket(request):
    return HttpResponse("Hello, world. You're at the basket index.")

def basket_detail(request, basket_id):
    return HttpResponse(f"This is basket {basket_id}")