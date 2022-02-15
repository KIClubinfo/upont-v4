from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import serializers

from .models import Club, Promotion, Student


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "id"]


class PromotionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Promotion
        fields = ["nickname"]


class StudentSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer()
    promo = PromotionSerializer()
    profile_url = serializers.SerializerMethodField()

    def get_profile_url(self, obj):
        return reverse("social:profile_viewed", args=(obj.user.pk,))

    picture_url = serializers.SerializerMethodField()

    def get_picture_url(self, obj):
        if obj.picture:
            return obj.picture.url
        else:
            return False

    class Meta:
        model = Student
        fields = ["user", "promo", "department", "profile_url", "picture_url"]


class ClubSerializer(
    serializers.HyperlinkedModelSerializer
):  # Not all fields yet as it is only used for posts
    logo_url = serializers.SerializerMethodField()

    def get_logo_url(self, obj):
        if obj.logo:
            return obj.logo.url
        else:
            return False

    background_picture_url = serializers.SerializerMethodField()

    def get_background_picture_url(self, obj):
        if obj.background_picture:
            return obj.background_picture.url
        else:
            return False

    class Meta:
        model = Club
        fields = ["name", "nickname", "logo_url", "background_picture_url"]
