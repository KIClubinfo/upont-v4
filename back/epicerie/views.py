from django.shortcuts import render, get_object_or_404

from .models import Basket

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the epicerie index.")

def basket(request):
    basket_list = Basket.objects.filter(is_active=True)
    output = ', '.join([str(basket) for basket in basket_list])
    return HttpResponse(output)

def basket_detail(request, basket_id):
    basket = get_object_or_404(Basket, pk=basket_id)
    return HttpResponse(f"This is basket {basket}, with composition {basket.composition}")