from rest_framework.viewsets import ModelViewSet

from .models import Bike
from .serializers import BikeSerializer


class BikesViewSet(ModelViewSet):
    serializer_class = BikeSerializer

    def get_queryset(self):
        return Bike.objects.all()
