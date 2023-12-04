from rest_framework import serializers

from social.serializers import UserSerializer

from .models import Basket, Basket_Order, Product, Vrac, Vrac_Order, Vegetable

class BasketSerializer(serializers.ModelSerializer):
    composition = serializers.SerializerMethodField()

    def get_composition(self, obj):
        return [str(vegetable) for vegetable in obj.composition.all()]
    
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
        model = Basket_Order
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
        return {product.name: product.price/100 for product in obj.ListProducts.all()}
    
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
    
    vrac = VracSerializer()
    
    class Meta:
        model = Vrac_Order
        fields = [
            "id",
            "student",
            "vrac",
            "order",
        ]

