from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Order, OrderItem, Vrac
from .serializers import (
    BikeSerializer,
    CreateOrderSerializer,
    OrderSummarySerializer,
    VracSerializer,
    VracUpdateSerializer
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
