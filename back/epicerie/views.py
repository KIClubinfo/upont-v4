from django.shortcuts import render, get_object_or_404

from .models import Basket

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the epicerie index.")

def basket(request):
    basket_list = Basket.objects.filter(is_active=True)
    return render(request, 'epicerie/basket_homepage.html', {'basket_list': basket_list})

def basket_detail(request, basket_id):
    basket = get_object_or_404(Basket, pk=basket_id)
    return HttpResponse(f"This is basket {basket}, with composition {basket.composition}")

def commander(request, basket_id):
    #on veut créer l'objet basket_order à partir de la requête
    basket = get_object_or_404(Basket, pk=basket_id)
    basket_order = Basket_Order(basket=basket, student=request.user, quantity=1)
    basket_order.save()
    return HttpResponse(f"Vous avez commandé le panier {basket} !")