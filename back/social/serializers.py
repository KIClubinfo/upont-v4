from django.contrib.auth.models import User
from django.templatetags.static import static
from django.urls import reverse
from rest_framework import serializers

from .models import Club, Membership, Promotion, Role, Student, Contact


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
        ]


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


class ContactSerializer(serializers.ModelSerializer):
    # If the contact is a student, use the student's data
    picture_url = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()

    def get_phone_number(self, obj):
        if obj.student and obj.student.phone_number:
            return obj.student.phone_number
        else:
            return obj.phone_number

    def get_email(self, obj):
        if obj.student and obj.student.user.email:
            return obj.student.user.email
        else:
            return obj.email

    def get_name(self, obj):
        if obj.student and obj.student.user.first_name and obj.student.user.last_name:
            return obj.student.user.first_name + " " + obj.student.user.last_name
        else:
            return obj.name

    def get_picture_url(self, obj):
        if obj.student and obj.student.picture:
            return obj.student.picture.url
        if obj.picture:
            return obj.picture.url
        else:
            return static("assets/img/user_default.png")

    class Meta:
        model = Contact
        fields = [
            "id",
            "name",
            "function",
            "email",
            "phone_number",
            "picture_url",
        ]
