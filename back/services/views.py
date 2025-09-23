from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from social.models import Membership

from .models import (
    Bike,
    Local,
    MedItem,
    Order,
    OrderItem,
    RequestForm,
    ReservationBike,
    ReservationMusicRoom,
    Vrac,
)
from .serializers import (
    BikeSerializer,
    CreateMusicRoomReservationSerializer,
    CreateOrderSerializer,
    LocalSerializer,
    MedItemSerializer,
    MedItemSummarySerializer,
    OrderSummarySerializer,
    RequestFormCreateSerializer,
    RequestFormListSerializer,
    ReservationBikeSerializer,
    ReservationMusicRoomSerializer,
    VracSerializer,
    VracUpdateSerializer,
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
        if not Membership.objects.filter(
            student__user=user, club__name="Ecoponts"
        ).exists():
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
        if not Membership.objects.filter(
            student__user=user, club__name="Ecoponts"
        ).exists():
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
            return Response(
                {"error": "Le produit n'existe pas"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response({"message": message}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Disable the default create method
        """
        return Response(
            {"error": "Method Not Allowed, Post data on /update_data"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


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
            user = request.user
            # Créer la commande
            order = Order.objects.create(name=user.username, id_user=user.id)

            # Pour chaque produit
            for product_name, total_quantity in zip(
                serializer.validated_data["products"],
                serializer.validated_data["total_quantities"],
            ):
                # Récupérer le produit
                vrac = Vrac.objects.get(name=product_name)

                # Générer les listes de prix et quantités
                prices = []
                quantities = []
                remaining_quantity = total_quantity

                for price, available in zip(vrac.price, vrac.stock_available):
                    if remaining_quantity <= 0:
                        break

                    quantity_from_this_batch = min(available, remaining_quantity)
                    prices.append(price)
                    quantities.append(quantity_from_this_batch)
                    remaining_quantity -= quantity_from_this_batch

                if remaining_quantity > 0:
                    raise ValueError

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
            # En cas d'erreur, le @transaction.atomic annulera toutes les
            # modifications
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def list_orders(self, request):
        """
        Returns a list of all orders with their summaries
        """
        user = request.user
        if Membership.objects.filter(
            student__user=user, club__name="Ecoponts"
        ).exists():
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
        return Membership.objects.filter(
            student__user=user, club__name="Ecoponts"
        ).exists()

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
        return Response(
            {"error": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class RequestFormViewSet(ModelViewSet):
    queryset = RequestForm.objects.all()

    def get_serializer_class(self):
        if self.action == "create_request":
            return RequestFormCreateSerializer
        return RequestFormListSerializer

    @action(detail=False, methods=["get"])
    def list_requests(self, request):
        """
        Returns a list of all RequestForm instances for a specific service
        based on the user's membership in a specific club.
        """
        user = request.user
        service = request.query_params.get("service")
        club_service_map = {
            "musique": "Décibel",
            "vracs": "Ecoponts",
            "velos": "Ecoponts",
            "med": "La Mediatek et Du Ponts et Des Jeux",
            "bde": "Bureau des élèves",
            "bds": "Bureau des sports",
            "bda": "Bureau des Arts",
            "foyer": "Foyer",
            "pep": "Ponts Etudes Projets",
            "ki": "Club Informatique",
            "trium": "Trium",
            "bitum": "BiTuM",
            "dvp": "Dévelop'Ponts",
            "jardin": "Ecoponts",
        }

        club_name = club_service_map.get(service)
        if (
            club_name
            and Membership.objects.filter(
                student__user=user, club__name=club_name
            ).exists()
        ):
            requests = RequestForm.objects.filter(service=service, status="pending")
        else:
            return Response(
                {"error": "Vous n'êtes pas autorisé à accéder à ces demandes"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RequestFormListSerializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def create_request(self, request):
        """
        Creates a new RequestForm instance with the status 'pending'
        """
        serializer = RequestFormCreateSerializer(data=request.data)
        if serializer.is_valid():
            RequestForm.objects.create(
                name=request.user.username,  # Assuming the user is authenticated
                status="pending",
                **serializer.validated_data,
            )
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
                return Response(
                    {"message": "Request marked as done"}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Request is not in 'pending' status"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except RequestForm.DoesNotExist:
            return Response(
                {"error": "RequestForm not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request, *args, **kwargs):
        """
        Disable the default create method
        """
        return Response(
            {"error": "Method Not Allowed, Post data on /update_data"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class ReservationBikeViewSet(ModelViewSet):
    serializer_class = ReservationBikeSerializer
    queryset = ReservationBike.objects.all()

    # Keep url_path='logs' if your frontend expects it, or change if desired
    @action(detail=False, methods=["post"])
    def get_nth_last_log(self, request):
        """
        Retrieves the string representation (str) of the N-th most recent
        ReservationBike instance associated with the given bike_id.
        """
        n_str = request.data.get("n")
        bike_id = request.data.get("bike_id")

        # --- Input Validation ---
        if bike_id is None:
            return Response(
                {"error": "Missing 'bike_id' in request body"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Attempt to convert bike_id to integer if needed, depending on your
        # Bike model's PK type
        try:
            bike_id_int = int(bike_id)
        except (ValueError, TypeError):
            return Response(
                {"error": "'bike_id' must be a valid integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if n_str is None:
            return Response(
                {"error": "Missing 'n' in request body"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            n = int(n_str)  # Convert n to integer
            if n <= 0:
                # N must be 1 or greater (1st last, 2nd last, etc.)
                raise ValueError("'n' must be a positive integer (1 or greater).")
        except (ValueError, TypeError):
            return Response(
                {"error": "'n' must be a positive integer (1 or greater)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # --- End Input Validation ---

        try:
            # --- Query Logic ---
            # 1. Filter by bike_id
            # 2. Order by start_date descending (most recent first)
            reservations_qs = ReservationBike.objects.filter(
                bike_id=bike_id_int
            ).order_by("-start_date")

            # Check if any reservations exist for this bike
            if not reservations_qs.exists():
                return Response(
                    {"error": f"No reservations found for bike_id {bike_id_int}"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # 3. Select the N-th item (using 0-based index n-1)
            # This directly fetches only the required object from the database

            # --- End Query Logic ---
            data = {}
            # 4. Get the string representation
            for i in range(min(n, reservations_qs.count())):
                reserv = reservations_qs[i]
                data[f"reservation_{i + 1}"] = str(reserv)

            # Use the key 'nth_last_log' as before, although the value is now
            # the reservation string
            return Response(data, status=status.HTTP_200_OK)

        except IndexError:
            # This occurs if n is greater than the total number of reservations found
            # E.g., asking for the 10th last when only 5 exist.
            count = (
                reservations_qs.count()
            )  # Get the count (efficient if already evaluated or needed here)
            return Response(
                {
                    "error": f"Cannot retrieve the {n}-th last reservation: Only {count} reservation(s) found for bike_id {bike_id_int}."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            # Log the actual error for debugging on the server
            print(
                f"Unexpected error in get_nth_last_log (str mode) for bike_id {bike_id_int}: {e}"
            )
            # Return a generic server error for the client
            return Response(
                {"error": "An unexpected server error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def log_reservation(self, request):
        """
        Creates or updates a log entry for the reservation of a bike
        """
        bike_id = request.data.get("bike_id")
        user = request.user

        try:
            bike = Bike.objects.get(pk=bike_id)
            last_log = (
                ReservationBike.objects.filter(bike=bike)
                .order_by("-start_date")
                .first()
            )

            if last_log and last_log.end_date is None:
                # Update the existing log entry
                last_log.end_date = timezone.now()
                last_log.save()
                serializer = ReservationBikeSerializer(last_log)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # Create a new log entry
                log = ReservationBike.objects.create(
                    bike=bike,
                    borrower_id=user.id,
                    name=user.username,
                    start_date=timezone.now(),
                    end_date=None,
                )
                serializer = ReservationBikeSerializer(log)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Bike.DoesNotExist:
            return Response(
                {"error": "Bike not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request, *args, **kwargs):
        """
        Disable the default create method
        """
        return Response(
            {"error": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class ReservationMusicRoomViewSet(ModelViewSet):
    serializer_class = ReservationMusicRoomSerializer
    queryset = ReservationMusicRoom.objects.all()

    @action(detail=False, methods=["get"])
    def upcoming_reservations(self, request):
        """
        Returns a list of all upcoming reservations
        """
        now = timezone.now()
        upcoming_reservations = ReservationMusicRoom.objects.filter(
            start_date__gt=now
        ).order_by("start_date")
        serializer = ReservationMusicRoomSerializer(upcoming_reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def create_reservation(self, request):
        """
        Creates a new reservation for the music room if there are no conflicts
        """
        serializer = CreateMusicRoomReservationSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            name = serializer.validated_data["name"]
            start_date = serializer.validated_data["start_date"]
            end_date = serializer.validated_data["end_date"]

            reservation = ReservationMusicRoom.objects.create(
                borrower_id=user.id, name=name, start_date=start_date, end_date=end_date
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
            if (
                reservation.borrower_id != request.user.id
                or Membership.objects.filter(
                    student__user=request.user, club__name="Décibel"
                ).exists()
            ):
                return Response(
                    {"error": "You are not authorized to cancel this reservation"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            reservation.delete()
            return Response(
                {"message": "Reservation cancelled successfully"},
                status=status.HTTP_200_OK,
            )
        except ReservationMusicRoom.DoesNotExist:
            return Response(
                {"error": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request, *args, **kwargs):
        """
        Disable the default create method
        """
        return Response(
            {"error": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class MedItemViewSet(ModelViewSet):
    serializer_class = MedItemSerializer
    queryset = MedItem.objects.all()

    @action(detail=True, methods=["post"])
    def borrow_item(self, request, pk=None):
        """
        Borrows an item if it is available
        """
        item = get_object_or_404(MedItem, pk=pk)
        user = request.user

        try:
            item.borrow(user.id)
            return Response(
                {"message": "Item borrowed successfully"}, status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def return_item(self, request, pk=None):
        """
        Returns an item if the user is the one who borrowed it or is a member of "La Mediatek et Du Ponts et Des Jeux"
        """
        item = get_object_or_404(MedItem, pk=pk)
        user = request.user

        if (
            item.borrowed_by != user.id
            and not Membership.objects.filter(
                student__user=user, club__name="La Mediatek et Du Ponts et Des Jeux"
            ).exists()
        ):
            return Response(
                {"error": "You are not authorized to return this item"},
                status=status.HTTP_403_FORBIDDEN,
            )

        item.return_item()
        return Response(
            {"message": "Item returned successfully"}, status=status.HTTP_200_OK
        )

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


class LocalViewSet(ModelViewSet):
    serializer_class = LocalSerializer
    queryset = Local.objects.all()

    LOCAL_CLUB_MAP = {
        "med": "La Mediatek et Du Ponts et Des Jeux",
        "ki": "Club Informatique",
        "musique": "Décibel",
        "bde": "Bureau des élèves",
        "bds": "Bureau des sports",
        "bda": "Bureau des Arts",
        "foyer": "Foyer",
        "pep": "Ponts Etudes Projets",
        "jardin": "Ecoponts",
        "dvp": "Dévelop'Ponts",
        "trium": "Trium",
        "bitum": "BiTuM",
    }

    @action(detail=False, methods=["post"])
    def change_status(self, request):
        """
        Changes the status (open/close) of a local if the user has the right permissions
        """
        user = request.user
        local_name = request.query_params.get("local")

        if not local_name:
            return Response(
                {"error": "Local name is required in query parameters"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the local exists and the user has permission
        try:
            local = get_object_or_404(Local, name=local_name)
            required_club = self.LOCAL_CLUB_MAP.get(local_name)

            if (
                not required_club
                or not Membership.objects.filter(
                    student__user=user, club__name=required_club
                ).exists()
            ):
                return Response(
                    {"error": "You are not authorized to change this local's status"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Toggle the status
            if local.is_open:
                local.close()
                message = f"{local.get_name_display()} est maintenant fermé"
            else:
                local.open()
                message = f"{local.get_name_display()} est maintenant ouvert"

            return Response({"message": message}, status=status.HTTP_200_OK)

        except Local.DoesNotExist:
            return Response(
                {"error": f"Local '{local_name}' not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["get"])
    def status(self, request):
        """
        Returns the status of all locals or a specific local if specified in query params
        """
        local_name = request.query_params.get("local")

        if local_name:
            local = get_object_or_404(Local, name=local_name)
            return Response({"status": str(local)}, status=status.HTTP_200_OK)

        # If no specific local requested, return all locals' status
        locals = Local.objects.all()
        status_dict = {local.name: str(local) for local in locals}
        return Response(status_dict, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def open_locals(self, request):
        """
        Returns a list of all open locals
        """
        open_locals = Local.objects.filter(is_open=True)
        serializer = LocalSerializer(open_locals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def available_locals(self, request):
        """
        Returns a list of closed locals that the user has permission to open
        """
        user = request.user

        # Get user's club memberships
        user_clubs = set(
            membership.club.name
            for membership in Membership.objects.filter(student__user=user)
        )

        # Get closed locals
        closed_locals = Local.objects.filter(is_open=False)

        # Filter locals based on user's permissions
        available_locals = [
            local
            for local in closed_locals
            if self.LOCAL_CLUB_MAP.get(local.name) in user_clubs
        ]

        serializer = LocalSerializer(available_locals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Disable the default create method
        """
        return Response(
            {"error": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
