from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from social.models import Student


from .models import Basket, BasketOrder, Vrac, VracOrder, Product, ProductOrder

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from rest_framework.views import APIView

# from rest_framework.response import Response

from .serializers import (
    BasketSerializer,
    BasketOrderSerializer,
    VracSerializer,
    VracOrderSerializer,
)


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

    queryset = BasketOrder.objects.all()
    serializer_class = BasketOrderSerializer
    http_method_names = ["get", "post"]

    def get_queryset(self):
        queryset = BasketOrder.objects.all()
        queryset = queryset.filter(student__user__id=self.request.user.id)
        return queryset

    def create(self, request, *args, **kwargs):
        # For each basket in the request, create a basket order
        for order in request.data["baskets"]:
            basket = Basket.objects.get(id=order["basket_id"])
            student = get_object_or_404(Student, user__id=request.user.id)
            quantity = order["quantity"]
            basket_order = BasketOrder(
                basket=basket, student=student, quantity=quantity
            )
            if basket_order.isValid():
                basket_order.save()
            else:
                return Response({"status": "error", "message": "Invalid basket order"})
        return Response({"status": "ok"})


class VracViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows vracs to be viewed.
    """

    http_method_names = ["get"]

    def get_queryset(self):
        queryset = Vrac.objects.all()
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        serializer = VracSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        vrac = get_object_or_404(queryset, pk=pk)
        serializer = VracSerializer(vrac)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        queryset = self.get_queryset()
        queryset = queryset.filter(is_active=True)
        latest_vrac = queryset.latest("pickup_date")
        serializer = VracSerializer(latest_vrac)
        return Response(serializer.data)


class VracOrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows vracs order to be viewed and created.
    POST request should be of the form:
    {
        "vrac_id": number,
        "listProducts":
            {
                "product_id": number,
                "quantity": number
            }[]
        
    }
    """
    http_method_names = ["get", "post"]
    serializer_class = VracOrderSerializer

    def get_queryset(self):
        queryset = VracOrder.objects.all()
        queryset = queryset.filter(student__user__id=self.request.user.id)
        return queryset
    
    def create(self, request):
        # Create the vrac order with the list of products and quantities
        # Or update the vrac order if it already exists
        student = get_object_or_404(Student, user__id=request.user.id)
        vrac = Vrac.objects.get(pk=request.data["vrac_id"])
        try :
            vrac_order = VracOrder.objects.get(vrac=vrac, student=student)
        except VracOrder.DoesNotExist:
            vrac_order = VracOrder(vrac=vrac, student=student)
        vrac_order.save()
        total = 0

        for productData in request.data["listProducts"]:
            productObject = get_object_or_404(Product, pk=productData["product_id"])
            if productData["quantity"] > 0:
                try :
                    prodOrder = ProductOrder.objects.get(product=productObject, vracOrder=vrac_order)
                    prodOrder.quantity = productData["quantity"]
                except ProductOrder.DoesNotExist:
                    prodOrder = ProductOrder(product=productObject, quantity=productData["quantity"], vracOrder=vrac_order)
                if not prodOrder.isValid():
                    return Response({"status": "error", "message": "Invalid product order"})
                prodOrder.save()
            # Add the price of the product to the total
            # Price is in cents per kg, qunatity is in grams
            total += (productObject.price) * (productData["quantity"] / 1000) 
            
        vrac_order.total = total
        vrac_order.save()
        return Response({"status": "ok"})
    
    @action(detail=False, methods=["get"])
    def hasOrdered(self, request):
        queryset = VracOrder.objects.all()
        queryset.filter(student__user__id=self.request.user.id)
        return Response(bool(queryset))
    
    @action(detail=False, methods=["get"])
    def latestVracOrder(self, request):
        queryset = VracOrder.objects.all()
        queryset = queryset.filter(student__user__id=self.request.user.id)
        try:
            latest_vrac_order = queryset.latest("vrac__pickup_date")
        except VracOrder.DoesNotExist:
            return Response({"status": "error", "message": "No vrac order found"})
        serializer = VracOrderSerializer(latest_vrac_order)
        return Response(serializer.data)
            

@login_required
def home(request):
    return render(request, "epicerie/epicerie.html")


@login_required
def basket(request):
    return render(request, "epicerie/basket.html")


@login_required
def vrac(request):
    return render(request, "epicerie/vrac.html")


@login_required
def recipes(request):
    return HttpResponse("This is the recettes page")
