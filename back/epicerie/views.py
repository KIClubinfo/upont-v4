from django.shortcuts import render, get_object_or_404

from .models import Basket, Basket_Order

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect


def index(request):
    return HttpResponse("Hello, world. You're at the epicerie index.")

def basket(request):
    basket_list = Basket.objects.filter(is_active=True)
    return render(request, 'epicerie/basket_homepage.html', {'basket_list': basket_list})

def basket_detail(request, basket_id):
    basket = get_object_or_404(Basket, pk=basket_id)
    return HttpResponse(f"This is basket {basket}, with composition {basket.composition}")

def basket_order(request):
    #on veut créer l'objet basket_order à partir de la requête
    basket_list = Basket.objects.filter(is_active=True)
    try:
        quantities = request.POST['basket']
    except (KeyError):
        quantities = [0 for basket in basket_list]
    for i, basket in enumerate(basket_list):
        if quantities[i] > 0:
            basket_order = Basket_Order(basket=basket, student=request.user.student , quantity=quantities[i])
            basket_order.save()

    return HttpResponseRedirect("/epicerie/panier/")