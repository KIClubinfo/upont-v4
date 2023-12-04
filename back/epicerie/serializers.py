from rest_framework.serializers import ModelSerializer 
from shop.models import Category
 
class CategorySerializer(ModelSerializer):
 
    class Product:
        model = Category
        fields = ['name', 'step', 'max', 'price']