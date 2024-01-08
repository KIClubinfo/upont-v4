from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from social.models import Student, Club, Membership

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

from .decorators import epicierOnly, studentIsEpicier
import csv

idEpicerie = 1


class BasketViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows baskets to be viewed.
    """

    queryset = Basket.objects.all()
    serializer_class = BasketSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = Basket.objects.all()
        return queryset
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        queryset = self.get_queryset()
        queryset = queryset.filter(is_active=True)
        return Response(BasketSerializer(queryset, many=True).data)


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
    
    @action(detail=False, methods=["get"])
    def export(self, request):
        baskets = Basket.objects.all()
        baskets = baskets.filter(is_active=True)
        queryset = BasketOrder.objects.all()
        queryset = queryset.filter(basket in baskets)
        response = HttpResponse(content_type='text/csv', 
                                headers={'Content-Disposition': 'attachment; filename="CommandesPanier.csv"'})
        writer = csv.writer(response)
        writer.writerow(['Nom', 'Prénom', 'Email', 'Téléphone', str(baskets[0]), str(baskets[1]), 'Total'])
        for order in queryset:
            writer.writerow([order.student.user.first_name,
                            order.student.user.last_name,
                            order.student.user.email,
                            order.student.phone_number,
                            order.quantity,
                            order.quantity,
                            order.total])


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

        # Modify / create the productOrder objects
        for productData in request.data["listProducts"]:
            productObject = get_object_or_404(Product, pk=productData["product_id"])
            try :
                prodOrder = ProductOrder.objects.get(product=productObject, vracOrder=vrac_order)
                if productData["quantity"] == 0:
                    prodOrder.delete()
                else:
                    prodOrder.quantity = productData["quantity"]
                    prodOrder.save()
            except ProductOrder.DoesNotExist:
                prodOrder = ProductOrder(product=productObject, quantity=productData["quantity"], vracOrder=vrac_order)
                if prodOrder.quantity > 0:
                    prodOrder.save()
            # Add the price of the product to the total
            # Price is in cents per kg, qunatity is in grams
            total += (productObject.price) * (productData["quantity"] / 1000) 
            
        vrac_order.total = total
        vrac_order.save()
        # Check if the vrac order is now empty after modification
        # If so, delete it.
        queryset = ProductOrder.objects.all()
        queryset.filter(vracOrder = vrac_order)
        if not (queryset):
            vrac_order.delete()
        return Response({"status": "ok"})
    
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
    
    @action(detail=False, methods=["post"])
    def deleteVracOrder(self, request):
        """
        Delete an order for the student making the request & the vrac_id
        """
        vracObject = Vrac.objects.get(pk = request.data["vracId"])
        student = get_object_or_404(Student, user__id=request.user.id)
        vrac_order = get_object_or_404(VracOrder, vrac = vracObject , student=student)
        vrac_order.delete()
        return Response({"status": "ok"})

@login_required
def home(request):
    isEpicier = studentIsEpicier(request.user)
    return render(request, "epicerie/epicerie.html", {"isEpicier": isEpicier})


@login_required
def basket(request):
    return render(request, "epicerie/basket.html")


@login_required
def vrac(request):
    return render(request, "epicerie/vrac.html")


@login_required
def recipes(request):
    return HttpResponse("This is the recettes page")

@epicierOnly()
def admin(request):
    return render(request, "epicerie/admin.html")
