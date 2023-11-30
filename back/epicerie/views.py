from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from social.models import Student

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

# from rest_framework.views import APIView
# from rest_framework.response import Response

from .models import Basket, Basket_Order
from .serializers import BasketSerializer, BasketOrderSerializer


class BasketViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows baskets to be viewed.
    """

    queryset = Basket.objects.all()
    serializer_class = BasketSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = Basket.objects.all()
        queryset = queryset.filter(is_active=True)
        return queryset

class BasketOrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows baskets order to be viewed and created.
    POST request should be of the form:
    {
        "baskets": [
            {
                "basket_id": 1,
                "quantity": 1
            },
            {
                "basket_id": 2,
                "quantity": 2
            }
        ]
    }
    """
    queryset = Basket_Order.objects.all()
    serializer_class = BasketOrderSerializer
    http_method_names = ["get", "post"]
    def get_queryset(self):
        queryset = Basket_Order.objects.all()
        return queryset

    def create(self, request, *args, **kwargs):
        # For each basket in the request, create a basket order
        for order in request.data["baskets"]:
            basket = Basket.objects.get(id=order["basket_id"])
            student = get_object_or_404(Student, user__id=request.user.id)
            quantity = order["quantity"]
            basket_order = Basket_Order(
                basket=basket, student=student, quantity=quantity
            )
            if basket_order.isValid():
                basket_order.save()
            else:
                return Response({"status": "error", "message": "Invalid basket order"})
        return Response({"status": "ok"})
        



@login_required
def home(request):
    return render(request, "epicerie/epicerie.html")


@login_required
def basket(request):
    basket_list = Basket.objects.filter(is_active=True)
    student = get_object_or_404(Student, user__id=request.user.id)
    student_baskets = Basket_Order.objects.filter(student=student)
    context = {"basket_list": basket_list, "student_baskets": student_baskets}
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
