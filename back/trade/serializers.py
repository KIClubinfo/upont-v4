from rest_framework import serializers
from social.serializers import StudentSerializer

from .models import Good, Transaction


class GoodSerializer(serializers.HyperlinkedModelSerializer):
    price = serializers.SerializerMethodField()

    def get_price(self, obj):
        return obj.price()

    class Meta:
        model = Good
        fields = ["name", "price", "id"]


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    good = GoodSerializer()
    student = StudentSerializer()
    date = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")

    class Meta:
        model = Transaction
        fields = ["good", "student", "quantity", "date", "id"]
