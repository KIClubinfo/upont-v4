from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Basket, Basket_Order
from social.models import Student

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect


def home(request):
    return render(request, 'epicerie/epicerie.html')

def basket(request):
    basket_list = Basket.objects.filter(is_active=True)
    return render(request, 'epicerie/basket.html', {'basket_list': basket_list})

def basket_detail(request, basket_id):
    basket = get_object_or_404(Basket, pk=basket_id)
    return HttpResponse(f"This is basket {basket}, with composition {basket.composition}")

@login_required
def basket_order(request):
    if request.method == 'POST':
        basket_list = Basket.objects.filter(is_active=True)
        student = get_object_or_404(Student, user__id=request.user.id)
        quantities = [0] * len(basket_list)
        try:
            quantities = request.POST.getlist('basket_quantity')
        except (KeyError):
            return HttpResponse("Error")
            
        for i, basket in enumerate(basket_list):
            if int(quantities[i]) > 0:
                basket_order = Basket_Order(basket=basket, student=student, quantity=int(quantities[i]))
                if basket_order.isValid():
                    basket_order.save()
                    print("I'm saving an order")
                else:
                    return HttpResponse("Error")

        return HttpResponseRedirect("/epicerie/panier/")
    

def vrac(request):
    return HttpResponse("This is the vrac page")

def recipes(request):
    return HttpResponse("This is the recettes page")