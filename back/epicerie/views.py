from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from social.models import Student, Club, Membership
from django.urls import reverse

from .models import Basket, BasketOrder, Vrac, VracOrder, Product, ProductOrder, Vegetable

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
        queryset.order_by("-pickup_date")
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
        queryset = BasketOrder.objects.all().filter(basket__is_active=True)
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
    @method_decorator(epicierOnly())
    def export(self, request):
        """
        Export the basket orders to a csv file
        """
        baskets = Basket.objects.filter(is_active=True)
        queryset = BasketOrder.objects.all()
        queryset = queryset.filter(basket__is_active=True)
        queryset.query.group_by = ['student_id']

        # Aggregate the basket orders by student
        ordersByStudent = {}
        for order in queryset:
            if order.student.id not in ordersByStudent.keys():
                ordersByStudent[order.student.id] = {}
            ordersByStudent[order.student.id][order.basket.id] = order.quantity

        print(ordersByStudent)
        # Create the csv file
        response = HttpResponse(content_type='text/csv', 
                                headers={'Content-Disposition': 'attachment; filename="CommandesPanier.csv"'})
        writer = csv.writer(response)
        headers = ['Nom', 'Prénom', 'Email', 'Téléphone']
        for basket in baskets:
            headers.append(str(basket))
        headers.append('Total (€)')
        writer.writerow(headers)
        for studentId, quantities in ordersByStudent.items():
            print(studentId)
            student = get_object_or_404(Student, pk=studentId)
            row = [student.user.last_name, student.user.first_name, student.user.email, student.phone_number]
            total = 0
            for basket in baskets:
                if basket.id in quantities.keys():
                    row.append(quantities[basket.id])
                    total += quantities[basket.id] * basket.price
                else:
                    row.append(0)
            row.append(total / 100)
            writer.writerow(row)
        return response


class VracViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows vracs to be viewed.
    """

    http_method_names = ["get"]

    def get_queryset(self):
        queryset = Vrac.objects.all()
        return queryset

    def list(self, request):
        pass

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
        queryset = VracOrder.objects.all().filter(vrac__is_active=True)
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
    
    @action(detail=False, methods=["get"])
    @method_decorator(epicierOnly())
    def export(self, request):
        """
        Export the vrac orders to a csv file
        """
        latest_vrac = Vrac.objects.filter(is_active=True).latest("pickup_date")
        queryset = VracOrder.objects.all()
        queryset = queryset.filter(vrac = latest_vrac)
        # Create the csv file
        response = HttpResponse(content_type='text/csv', 
                                headers={'Content-Disposition': 'attachment; filename="CommandesVrac.csv"'})
        writer = csv.writer(response)
        headers = ['Nom', 'Prénom', 'Email', 'Téléphone', 'Total (€)']
        # Dictionnary to keep track of the column index of each product
        productToColumn = {}
        for product in Product.objects.filter(vrac=latest_vrac):
            productToColumn[product] = len(headers)
            headers.append(product.name)
        writer.writerow(headers)
        # Add the data for each student
        for vracOrder in queryset:
            student = vracOrder.student
            row = [0 for i in range(len(headers))]
            row[0] = student.user.last_name
            row[1] = student.user.first_name
            row[2] = student.user.email
            row[3] = student.phone_number
            row[4] = vracOrder.total / 100
            productOrders = ProductOrder.objects.filter(vracOrder=vracOrder)
            for productOrder in productOrders:
                row[productToColumn[productOrder.product]] = productOrder.quantity
            writer.writerow(row)
        
        return response

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


@epicierOnly()
def uploadVrac(request):
    if request.method == 'POST':
        try:
            file = request.FILES["file"]
            if not file.name.endswith('.csv'):
                context = {"message": "Le fichier doit être au format csv"}
                return render(request, "epicerie/uploadResults.html", context)
            #if file is too large, return
            if file.multiple_chunks():
                context = {"message": "Le fichier est trop gros"}
                return render(request, "epicerie/uploadResults.html", context)
            # Set all the old vracs to inactive
            Vrac.objects.all().update(is_active=False)
            #read the file
            vrac = Vrac(
                open_date = request.POST["openDate"],
                close_date = request.POST["closeDate"],
                pickup_date = request.POST["pickupDate"],
                is_active = True
            )
            file_data = file.read().decode("utf-8")
            lines = file_data.split("\n")
            for (i,line) in enumerate(lines):
                if i == 0:
                    correspondance = {}
                    fields = line.split(",")
                    correspondance["Maximum"] = fields.index("Maximum")
                    correspondance["Step"] = fields.index("Step")
                    correspondance["Produit"] = fields.index("Produit")
                    correspondance["Prix"] = fields.index("Prix/Kg(€)")
                    print(correspondance)
                    vrac.save()
                else:
                    if line == "":
                        continue
                    fields = line.split(",")
                    product = Product(
                        vrac = vrac,
                        name = fields[correspondance["Produit"]],
                        price = int(fields[correspondance["Prix"]]) * 100,
                        max = fields[correspondance["Maximum"]],
                        step = fields[correspondance["Step"]]
                    )
                    product.save()
            context = {"message": "Mis en ligne avec succès"}
            return render(request, "epicerie/uploadResults.html", context)
        except Exception as e:
            print
            context = {"message": "Erreur lors de la mise en ligne"}
            return render(request, "epicerie/uploadResults.html", context)
    else:
        return redirect(reverse("epicerie:admin"))


@epicierOnly()
def uploadBasket(request):
    if request.method == "POST":
        file = request.FILES["file"]
        if not file.name.endswith('.csv'):
            return redirect(reverse("epicerie:admin"))
        #if file is too large, return
        if file.multiple_chunks():
            return redirect(reverse("epicerie:admin"))  
        try:
            Basket.objects.all().update(is_active=False)
            #read the file
            file_data = file.read().decode("utf-8")
            lines = file_data.split("\n")
            #We create baskets from the first line of the file
            headers = lines[0].split(",")
            prices = headers[2:]
            baskets = [
                Basket(
                    price = int(price) * 100,
                    open_date = request.POST["openDate"],
                    close_date = request.POST["closeDate"],
                    pickup_date = request.POST["pickupDate"],
                    is_active = True
                ) for price in prices
            ]
            # Save them to the database
            for basket in baskets:
                basket.save()
            # We then add the vegetables to the baskets
            for i in range(1, len(lines)):
                if lines[i] == "":
                    continue
                fields = lines[i].split(",")
                isInBasket = fields[2:]
                for (i, word) in enumerate(isInBasket):
                    if word == "Oui" or word == "oui" or word == "OUI":
                        vegetable = Vegetable(
                            basket = baskets[i],
                            name = fields[0],
                            quantity = int(fields[1])
                        )
                        vegetable.save()
            context = {"message": "Mis en ligne avec succès"}
            return render(request, "epicerie/uploadResults.html", context)

        except Exception as e:
            context = {"message": "Erreur lors de la mise en ligne"}
            return render(request, "epicerie/uploadResults.html", context)
   
    return redirect(reverse("epicerie:admin"))




