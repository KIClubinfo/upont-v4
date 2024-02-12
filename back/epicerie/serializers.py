from rest_framework import serializers

from .models import (
    Basket,
    BasketOrder,
    Product,
    Vrac,
    VracOrder,
    ProductOrder,
    Vegetable,
)


class BasketSerializer(serializers.ModelSerializer):
    composition = serializers.SerializerMethodField()

    def get_composition(self, obj):
        return [
            {"id": vegetable.id, "name": vegetable.name, "quantity": vegetable.quantity}
            for vegetable in Vegetable.objects.filter(basket=obj)
        ]

    class Meta:
        model = Basket
        fields = [
            "id",
            "price",
            "composition",
            "open_date",
            "close_date",
            "pickup_date",
            "is_active",
        ]


class BasketSerializerLite(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = [
            "id",
            "price",
            "pickup_date",
        ]


class BasketOrderSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()

    def get_student(self, obj):
        simplified_student = {}
        simplified_student["id"] = obj.student.id
        simplified_student["first_name"] = obj.student.user.first_name
        simplified_student["last_name"] = obj.student.user.last_name
        simplified_student["email"] = obj.student.user.email
        simplified_student["phone_number"] = obj.student.phone_number
        return simplified_student

    basket = BasketSerializerLite()

    class Meta:
        model = BasketOrder
        fields = [
            "id",
            "student",
            "basket",
            "quantity",
        ]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "step",
            "max",
            "price",
        ]


class VracSerializer(serializers.ModelSerializer):
    ListProducts = serializers.SerializerMethodField()

    def get_ListProducts(self, obj):
        return [
            ProductSerializer(product).data
            for product in Product.objects.filter(vrac=obj)
        ]

    class Meta:
        model = Vrac
        fields = [
            "id",
            "ListProducts",
            "open_date",
            "close_date",
            "pickup_date",
            "is_active",
        ]


class VracSerializerLite(serializers.ModelSerializer):
    class Meta:
        model = Vrac
        fields = [
            "id",
            "pickup_date",
        ]


class VracOrderSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()

    def get_student(self, obj):
        simplified_student = {}
        simplified_student["id"] = obj.student.id
        simplified_student["first_name"] = obj.student.user.first_name
        simplified_student["last_name"] = obj.student.user.last_name
        simplified_student["email"] = obj.student.user.email
        simplified_student["phone_number"] = obj.student.phone_number
        return simplified_student

    vrac = VracSerializerLite()

    order = serializers.SerializerMethodField()

    def get_order(self, obj):
        return [
            {
                "id": prodOrder.product.id,
                "product": prodOrder.product.name,
                "quantity": prodOrder.quantity,
            }
            for prodOrder in ProductOrder.objects.filter(vracOrder__pk=obj.id)
        ]

    class Meta:
        model = VracOrder
        fields = [
            "id",
            "student",
            "vrac",
            "order",
            "total",
        ]
