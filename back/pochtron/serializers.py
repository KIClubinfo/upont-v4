from rest_framework import serializers

from .models import Alcohol


class AlcoholSerializer(serializers.HyperlinkedModelSerializer):
    price = serializers.SerializerMethodField()

    def get_price(self, obj):
        return obj.price()

    class Meta:
        model = Alcohol
        fields = ["name", "degree", "volume", "price", "id"]
