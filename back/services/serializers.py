from rest_framework import serializers
from .models import Bike


class BikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bike
        fields = ['id', 'name', 'is_borrowed', 'borrower_id']
