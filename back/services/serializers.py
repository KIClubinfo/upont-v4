from rest_framework import serializers
from datetime import timedelta
from .models import Bike, Order, OrderItem, Vrac, RequestForm, ReservationBike, ReservationMusicRoom, Mediatek, MedItem


class BikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bike
        fields = ["id", "name", "is_borrowed", "borrower_id"]


class VracSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vrac
        fields = ["id", "name", "type", "price", "stock", "stock_available"]

class VracUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    type = serializers.ChoiceField(choices=[("vrac", "Vrac"), ("unite", "Unité")])
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField(min_value=0)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "name", "products", "prices", "quantity"]


class CreateOrderSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    products = serializers.ListField(child=serializers.CharField(max_length=100))
    prices = serializers.ListField(
        child=serializers.ListField(
            child=serializers.DecimalField(max_digits=10, decimal_places=2)
        )
    )
    quantities = serializers.ListField(
        child=serializers.ListField(child=serializers.IntegerField(min_value=0))
    )

    def validate(self, data):
        if not (
            len(data["products"]) == len(data["prices"]) == len(data["quantities"])
        ):
            raise serializers.ValidationError(
                "Les listes products, prices et quantities doivent avoir la même taille"
            )

        if "Thé" in data["products"]:
            raise serializers.ValidationError(
                {"error": "I'm an epicier, not a teapot!"}, code=418
            )

        # Vérifier que chaque produit existe
        for product_name in data["products"]:
            if not Vrac.objects.filter(name=product_name).exists():
                raise serializers.ValidationError(
                    f"Le produit {product_name} n'existe pas"
                )

        return data


class OrderSummarySerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    total_quantities = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "name", "products", "total_quantities", "total_price"]

    def get_products(self, obj):
        return [item.vrac.name for item in obj.orderitem_set.all()]

    def get_total_quantities(self, obj):
        return [sum(item.quantities) for item in obj.orderitem_set.all()]

    def get_total_price(self, obj):
        return obj.get_total_price()

class RequestFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestForm
        fields = ["message", "service"]

class RequestFormCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestForm
        fields = ["message", "service"]

class RequestFormListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestForm
        fields = ["id", "name", "message", "service", "status"]

class ReservationBikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationBike
        fields = ["id", "bike", "borrower_id", "name", "start_date", "end_date"]

class ReservationMusicRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationMusicRoom
        fields = ["id", "borrower_id", "name", "start_date", "end_date"]

class CreateMusicRoomReservationSerializer(serializers.Serializer):
    borrower_id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    start_date = serializers.DateTimeField()
    duration = serializers.IntegerField(min_value=1)

    def validate(self, data):
        start_date = data["start_date"]
        end_date = start_date + timedelta(hours=data["duration"])

        # Check for conflicts
        if ReservationMusicRoom.objects.filter(
            start_date__lt=end_date, end_date__gt=start_date
        ).exists():
            raise serializers.ValidationError("There is a conflict with an existing reservation.")

        return data


class MediatekSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mediatek
        fields = ["is_open"]

class MedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedItem
        fields = ["id", "type", "title", "author", "year", "is_available", "description", "image", "borrowed_by", "borrowed_date"]

class MedItemSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedItem
        fields = ["id", "name", "type", "is_available"]