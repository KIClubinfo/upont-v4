from django.contrib.auth.decorators import login_required

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from social.models import Student

from .models import Basket, Basket_Order


@login_required
def home(request):
    return render(request, "epicerie/epicerie.html")


@login_required
def basket(request):
    basket_list = Basket.objects.filter(is_active=True)
    context = {"basket_list": basket_list}
    return render(request, "epicerie/basket.html", context)


@login_required
def basket_detail(request, basket_id):
    basket = get_object_or_404(Basket, pk=basket_id)
    return HttpResponse(
        f"This is basket {basket}, with composition {basket.composition}"
    )


@login_required
def basket_order(request):
    if request.method == "POST":
        basket_list = Basket.objects.filter(is_active=True)
        student = get_object_or_404(Student, user__id=request.user.id)
        try:
            quantities = request.POST.getlist("basket_quantity")
        except KeyError:
            quantities = [0] * len(basket_list)

        for i, basket in enumerate(basket_list):
            if int(quantities[i]) > 0:
                basket_order = Basket_Order(
                    basket=basket, student=student, quantity=int(quantities[i])
                )
                if basket_order.isValid():
                    basket_order.save()
                    print("I'm saving an order")
                else:
                    return HttpResponse("Error")

        return HttpResponseRedirect("/epicerie/panier/")


@login_required
def vrac(request):
    return HttpResponse("This is the vrac page")


@login_required
def recipes(request):
    return HttpResponse("This is the recettes page")
