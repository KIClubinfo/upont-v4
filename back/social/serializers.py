from django.contrib.auth.models import User
from django.templatetags.static import static
from django.urls import reverse
from rest_framework import serializers

from .models import Club, Membership, Promotion, Role, Student


class UserSerializer(serializers.HyperlinkedModelSerializer):
    last_login = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"])
    date_joined = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"])

    class Meta:
        model = User
        fields = ["first_name", "last_name", "id", "last_login", "date_joined"]


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
            return static("assets/img/user_default.png")

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "promo",
            "department",
            "profile_url",
            "picture_url",
            "birthdate",
            "biography",
            "phone_number",
            "gender",
            "first_connection",
            "is_validated",
            "is_moderator",
        ]

    birthdate = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"])


class RoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = ["name", "id"]


class MembershipSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    role = RoleSerializer()

    class Meta:
        model = Membership
        fields = ["student", "is_admin", "is_old", "role"]


class ClubSerializer(
    serializers.HyperlinkedModelSerializer
):  # Not all fields yet as it is only used for posts
    logo_url = serializers.SerializerMethodField()

    def get_logo_url(self, obj):
        if obj.logo:
            return obj.logo.url
        else:
            return static("assets/img/logo_default.png")

    background_picture_url = serializers.SerializerMethodField()

    def get_background_picture_url(self, obj):
        if obj.background_picture:
            return obj.background_picture.url
        else:
            return False

    def get_id(self, obj):
        return obj.pk

    members = MembershipSerializer(source="membership_set", many=True)

    class Meta:
        model = Club
        fields = [
            "id",
            "name",
            "nickname",
            "logo_url",
            "background_picture_url",
            "members",
            "label",
        ]


class ClubSerializerLite(
    serializers.HyperlinkedModelSerializer
):  # Not all fields yet as it is only used for posts
    logo_url = serializers.SerializerMethodField()

    def get_logo_url(self, obj):
        if obj.logo:
            return obj.logo.url
        else:
            return static("assets/img/logo_default.png")

    background_picture_url = serializers.SerializerMethodField()

    def get_background_picture_url(self, obj):
        if obj.background_picture:
            return obj.background_picture.url
        else:
            return False

    def get_id(self, obj):
        return obj.pk

    class Meta:
        model = Club
        fields = [
            "id",
            "name",
            "nickname",
            "logo_url",
            "background_picture_url",
            "label",
        ]
