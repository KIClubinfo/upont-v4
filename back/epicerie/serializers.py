from rest_framework import serializers

from .models import Basket, Vegetable



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
       



