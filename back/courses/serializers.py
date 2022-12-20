from rest_framework import serializers

from .models import Course, Teacher


class TeacherSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Teacher
        fields = [
            "id",
            "name",
        ]


class CourseSerializer(serializers.HyperlinkedModelSerializer):
    teacher = TeacherSerializer()

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "acronym",
            "department",
            "teacher",
            "description",
        ]
