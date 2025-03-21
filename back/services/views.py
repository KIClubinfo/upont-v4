from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.exceptions import ValidationError
from datetime import timedelta
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


from .models import Bike, Order, OrderItem, Vrac, RequestForm, ReservationBike, ReservationMusicRoom, Mediatek, MedItem
from social.models import Membership

from .serializers import (
    BikeSerializer,
    CreateOrderSerializer,
    OrderSummarySerializer,
    VracSerializer,
    VracUpdateSerializer,
    RequestFormSerializer,
    ReservationBikeSerializer,
    ReservationMusicRoomSerializer,
    CreateMusicRoomReservationSerializer,
    MediatekSerializer,
    MedItemSerializer,
    MedItemSummarySerializer
)


class BikesViewSet(ModelViewSet):
    serializer_class = BikeSerializer

    def get_queryset(self):
        return Bike.objects.all()


class VracViewSet(ModelViewSet):
    serializer_class = VracSerializer
    queryset = Vrac.objects.all()

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def update_stock(self, request):
        """
        Vérifie si l'utilisateur est membre d'Ecoponts et met à jour le stock
        """
        user = request.user

        # Vérifier si l'utilisateur est membre d'Ecoponts
        if not Membership.objects.filter(student__user=user, club__name="Ecoponts").exists():
            return Response(
                {"error": "Vous n'êtes pas autorisé à effectuer cette opération"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Valider les données d'entrée
        serializer = VracUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        name = serializer.validated_data["name"]
        type = serializer.validated_data["type"]
        price = serializer.validated_data["price"]
        quantity = serializer.validated_data["quantity"]

        try:
            # Vérifier si le produit existe
            vrac = Vrac.objects.get(name=name)
            # Ajouter au stock existant
            vrac.add_stock([price], [quantity])
            message = f"Le stock de {name} a été mis à jour avec succès"
        except Vrac.DoesNotExist:
            # Créer un nouveau produit
            Vrac.objects.create(
                name=name,
                type=type,
                price=[price],
                stock=[quantity],
                stock_available=[quantity],
            )
            message = f"Le produit {name} a été créé avec succès"

        return Response({"message": message}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["post"])
    @transaction.atomic
    def regularize_stock(self, request):
        """
        Vérifie si l'utilisateur est membre d'Ecoponts et met à jour le stock
        """
        user = request.user

        # Vérifier si l'utilisateur est membre d'Ecoponts
        if not Membership.objects.filter(student__user=user, club__name="Ecoponts").exists():
            return Response(
                {"error": "Vous n'êtes pas autorisé à effectuer cette opération"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Valider les données d'entrée
        serializer = VracUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        name = serializer.validated_data["name"]
        quantity = serializer.validated_data["quantity"]

        try:
            # Vérifier si le produit existe
            vrac = Vrac.objects.get(name=name)
            # Ajouter au stock existant
            vrac.update_quantity(quantity)
            message = f"Le stock de {name} a été mis à jour avec succès"
        except Vrac.DoesNotExist:
            # Créer un nouveau produit
            return Response({"error": "Le produit n'existe pas"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": message}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Disable the default create method
        """
        return Response({"error": "Method Not Allowed, Post data on /update_data"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



class OrderViewSet(ModelViewSet):
    serializer_class = OrderSummarySerializer
    queryset = Order.objects.all()

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def create_order(self, request):
        """
        Crée une commande avec plusieurs produits
        """
        serializer = CreateOrderSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Créer la commande
            order = Order.objects.create(name=serializer.validated_data["name"])

            # Pour chaque produit
            for product_name, prices, quantities in zip(
                serializer.validated_data["products"],
                serializer.validated_data["prices"],
                serializer.validated_data["quantities"],
            ):
                # Récupérer le produit
                vrac = Vrac.objects.get(name=product_name)

                # Réduire le stock disponible
                vrac.reduce_stock_available(prices, quantities)

                # Créer l'OrderItem
                OrderItem.objects.create(
                    order=order, vrac=vrac, prices=prices, quantities=quantities
                )

            return Response(
                {
                    "id": order.id,
                    "name": order.name,
                    "total_price": order.get_total_price(),
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            # En cas d'erreur, le @transaction.atomic annulera toutes les modifications
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def list_orders(self, request):
        """
        Returns a list of all orders with their summaries
        """
        user = request.user
        if Membership.objects.filter(student__user=user, club__name="Ecoponts").exists():
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(id_user=user.id)
        
        serializer = OrderSummarySerializer(orders, many=True)
        return Response(serializer.data)

    def has_permission(self, user, order):
        # Check if the user is the owner of the order
        if order.id_user == user.id:
            return True
        # Check if the user has a membership in the club "Ecoponts"
        return Membership.objects.filter(student__user=user, club__name="Ecoponts").exists()

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def confirm_order(self, request, pk=None):
        """
        Confirme une commande, réduit les stocks et supprime la commande
        """
        try:
            # Récupérer la commande
            order = self.get_object()
            
            if not self.has_permission(request.user, order):
                return Response(
                    {"error": "Vous n'êtes pas autorisé à confirmer cette commande"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Pour chaque item de la commande
            for order_item in order.orderitem_set.all():
                # Réduire le stock du produit
                order_item.vrac.reduce_stock(order_item.prices, order_item.quantities)

            # Sauvegarder le nom pour le message de retour
            order_name = order.name

            # Supprimer la commande
            order.delete()

            return Response(
                {"message": f"Commande {order_name} confirmée et traitée avec succès"},
                status=status.HTTP_200_OK,
            )

        except Order.DoesNotExist:
            return Response(
                {"error": "Commande non trouvée"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def cancel_order(self, request, pk=None):
        """
        Annule une commande, restaure les stocks disponibles et supprime la commande
        """
        try:
            # Récupérer la commande
            order = self.get_object()

            if not self.has_permission(request.user, order):
                return Response(
                    {"error": "Vous n'êtes pas autorisé à confirmer cette commande"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Pour chaque item de la commande
            for order_item in order.orderitem_set.all():
                # Restaurer le stock disponible du produit
                order_item.vrac.add_stock_available(
                    order_item.prices, order_item.quantities
                )

            # Sauvegarder le nom pour le message de retour
            order_name = order.name

            # Supprimer la commande
            order.delete()

            return Response(
                {"message": f"Commande {order_name} annulée avec succès"},
                status=status.HTTP_200_OK,
            )

        except Order.DoesNotExist:
            return Response(
                {"error": "Commande non trouvée"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    def create(self, request, *args, **kwargs):
        """
        Disable the default create method
        """
        return Response({"error": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

class RequestFormViewSet(ModelViewSet):
    serializer_class = RequestFormSerializer
    queryset = RequestForm.objects.all()

    @action(detail=False, methods=["get"])
    def list_requests(self, request):
        """
        Returns a list of all RequestForm instances for a specific service
        based on the user's membership in a specific club.
        """
        user = request.user
        service = request.query_params.get("service")

        if service == "musique" and Membership.objects.filter(student__user=user, club__name="Décibel").exists():
            requests = RequestForm.objects.filter(service="musique", status="pending")
        elif service in ["vracs", "velos"] and Membership.objects.filter(student__user=user, club__name="Ecoponts").exists():
            requests = RequestForm.objects.filter(service=service, status="pending")
        else:
            return Response(
                {"error": "Vous n'êtes pas autorisé à accéder à ces demandes"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RequestFormSerializer(requests, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=["post"])
    def create_request(self, request):
        """
        Creates a new RequestForm instance with the status 'pending'
        """
        serializer = RequestFormSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(status="pending")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def mark_as_done(self, request, pk=None):
        """
        Changes the status of a RequestForm instance from 'pending' to 'done'
        """
        try:
            request_form = self.get_object()
            if request_form.status == "pending":
                request_form.status = "done"
                request_form.save()
                return Response({"message": "Request marked as done"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Request is not in 'pending' status"}, status=status.HTTP_400_BAD_REQUEST)
        except RequestForm.DoesNotExist:
            return Response({"error": "RequestForm not found"}, status=status.HTTP_404_NOT_FOUND)
    def create(self, request, *args, **kwargs):
        """
        Disable the default create method
        """
        return Response({"error": "Method Not Allowed, Post data on /update_data"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
class ReservationBikeViewSet(ModelViewSet):
    serializer_class = ReservationBikeSerializer
    queryset = ReservationBike.objects.all()

    @action(detail=True, methods=["post"])
    def get_nth_last_log(self, request, pk=None):
        """
        Returns the n-th last line of the logs of the reservation of bike with the given id
        """
        serializer = ReservationBikeSerializer(data=request.data)
        if serializer.is_valid():
            n = serializer.validated_data["n"]
            try:
                reservation = self.get_object()
                logs = reservation.logs.splitlines()
                if n > len(logs):
                    n = len(logs)
                nth_last_log = logs[-n]
                data = {}
                for i in range(len(nth_last_log)):
                    data[i] = str(nth_last_log[i])
                return Response(data, status=status.HTTP_200_OK)
            except ReservationBike.DoesNotExist:
                return Response({"error": "ReservationBike not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=False, methods=["post"])
    def create_log(self, request):
        """
        Creates a new log entry for the reservation of a bike
        """
        bike_id = request.data.get("bike_id")
        name = request.data.get("name")
        try:
            bike = Bike.objects.get(pk=bike_id)
            log = ReservationBike.objects.create(
                bike=bike,
                name=name,
                start_date=timezone.now(),
                end_date=None
            )
            serializer = ReservationBikeSerializer(log)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Bike.DoesNotExist:
            return Response({"error": "Bike not found"}, status=status.HTTP_404_NOT_FOUND)
    @action(detail=False, methods=["post"])
    def update_log(self, request):
        """
        Updates an existing log entry for the reservation of a bike by setting end_date to now
        """
        bike_id = request.data.get("bike_id")
        name = request.data.get("name")
        try:
            log = ReservationBike.objects.get(bike_id=bike_id, name=name, end_date__isnull=True)
            log.end_date = timezone.now()
            log.save()
            serializer = ReservationBikeSerializer(log)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ReservationBike.DoesNotExist:
            return Response({"error": "Active reservation not found"}, status=status.HTTP_404_NOT_FOUND)
    def create(self, request, *args, **kwargs):
        """
        Disable the default create method
        """
        return Response({"error": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
class ReservationMusicRoomViewSet(ModelViewSet):
    serializer_class = ReservationMusicRoomSerializer
    queryset = ReservationMusicRoom.objects.all()

    @action(detail=False, methods=["get"])
    def upcoming_reservations(self, request):
        """
        Returns a list of all upcoming reservations
        """
        now = timezone.now()
        upcoming_reservations = ReservationMusicRoom.objects.filter(start_date__gt=now).order_by('start_date')
        serializer = ReservationMusicRoomSerializer(upcoming_reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def create_reservation(self, request):
        """
        Creates a new reservation for the music room if there are no conflicts
        """
        serializer = CreateMusicRoomReservationSerializer(data=request.data)
        if serializer.is_valid():
            borrower_id = serializer.validated_data["borrower_id"]
            name = serializer.validated_data["name"]
            start_date = serializer.validated_data["start_date"]
            duration = serializer.validated_data["duration"]
            end_date = start_date + timedelta(hours=duration)

            reservation = ReservationMusicRoom.objects.create(
                borrower_id=borrower_id,
                name=name,
                start_date=start_date,
                end_date=end_date
            )
            reservation_serializer = ReservationMusicRoomSerializer(reservation)
            return Response(reservation_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=["post"])
    def cancel_reservation(self, request, pk=None):
        """
        Cancels a reservation for the music room if the user is the one who created it
        """
        try:
            reservation = self.get_object()
            if reservation.borrower_id != request.user.id:
                return Response({"error": "You are not authorized to cancel this reservation"}, status=status.HTTP_403_FORBIDDEN)
            reservation.delete()
            return Response({"message": "Reservation cancelled successfully"}, status=status.HTTP_200_OK)
        except ReservationMusicRoom.DoesNotExist:
            return Response({"error": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND)
    def create(self, request, *args, **kwargs):
        """
        Disable the default create method
        """
        return Response({"error": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
class MediatekViewSet(ModelViewSet):
    serializer_class = MediatekSerializer
    queryset = Mediatek.objects.all()

    @action(detail=False, methods=["post"])
    def open_mediatek(self, request):
        """
        Opens the mediatek if the user is a member of "La Mediatek et Du Ponts et Des Jeux"
        """
        user = request.user
        if not Membership.objects.filter(student__user=user, club__name="La Mediatek et Du Ponts et Des Jeux").exists():
            return Response({"error": "Vous n'êtes pas autorisé à effectuer cette opération"}, status=status.HTTP_403_FORBIDDEN)

        mediatek = get_object_or_404(Mediatek)
        mediatek.open()
        return Response({"message": "La mediatek est maintenant ouverte"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def close_mediatek(self, request):
        """
        Closes the mediatek if the user is a member of "La Mediatek et Du Ponts et Des Jeux"
        """
        user = request.user
        if not Membership.objects.filter(student__user=user, club__name="La Mediatek et Du Ponts et Des Jeux").exists():
            return Response({"error": "Vous n'êtes pas autorisé à effectuer cette opération"}, status=status.HTTP_403_FORBIDDEN)

        mediatek = get_object_or_404(Mediatek)
        mediatek.close()
        return Response({"message": "La mediatek est maintenant fermée"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["get"])
    def status(self, request):
        """
        Returns the status of the mediatek (open or closed)
        """
        mediatek = get_object_or_404(Mediatek)
        status = str(mediatek)
        return Response({"status": status}, status=status.HTTP_200_OK)
    def create(self, request, *args, **kwargs):
        """
        Disable the default create method
        """
        return Response({"error": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class MedItemViewSet(ModelViewSet):
    serializer_class = MedItemSerializer
    queryset = MedItem.objects.all()

    @action(detail=True, methods=["post"])
    def borrow_item(self, request, pk=None):
        """
        Borrows an item if it is available
        """
        item = get_object_or_404(MedItem, pk=pk)
        borrower_id = request.data.get("borrower_id")

        if not borrower_id:
            return Response({"error": "Borrower ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item.borrow(borrower_id)
            return Response({"message": "Item borrowed successfully"}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def return_item(self, request, pk=None):
        """
        Returns an item if the user is the one who borrowed it or is a member of "La Mediatek et Du Ponts et Des Jeux"
        """
        item = get_object_or_404(MedItem, pk=pk)
        returner_id = request.data.get("returner_id")

        if not returner_id:
            return Response({"error": "Returner ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        if item.borrowed_by != returner_id and not Membership.objects.filter(student__user=request.user, club__name="La Mediatek et Du Ponts et Des Jeux").exists():
            return Response({"error": "You are not authorized to return this item"}, status=status.HTTP_403_FORBIDDEN)

        item.return_item()
        return Response({"message": "Item returned successfully"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["get"])
    def detail(self, request, pk=None):
        """
        Returns all the information of a MedItem
        """
        item = get_object_or_404(MedItem, pk=pk)
        serializer = MedItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["get"])
    def filter(self, request):
        """
        Filters the MedItem database based on type and availability
        """
        item_type = request.query_params.get("type", None)
        available = request.query_params.get("available", None)

        filters = Q()
        if item_type:
            filters &= Q(type=item_type)
        if available is not None:
            if available == "1":
                filters &= Q(is_available=True)
            elif available == "0":
                filters &= Q(is_available=False)

        items = MedItem.objects.filter(filters)
        serializer = MedItemSummarySerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
