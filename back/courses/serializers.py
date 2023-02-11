from rest_framework import serializers

from .models import Course, Group, Resource, Teacher, Timeslot


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
            "old_courses",
            "posts",
        ]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    teacher = TeacherSerializer()

    class Meta:
        model = Group
        fields = [
            "course",
            "teacher",
            "number",
            "students",
        ]


class TimeslotSerializer(serializers.HyperlinkedModelSerializer):
    # course_groups = GroupSerializer()

    def get_course_name(self, obj):
        if obj.course_groups.exists():
            return obj.course_groups.first().course.name
        else:
            return ""

    course_name = serializers.SerializerMethodField()

    class Meta:
        model = Timeslot
        fields = [
            "id",
            "start",
            "end",
            "course_groups",
            "course_name",
            "place",
        ]


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Resource
        fields = [
            "id",
            "name",
            "author",
            "date",
            "file",
            "post",
        ]
