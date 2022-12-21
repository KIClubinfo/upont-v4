from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from social.models import Student

from .models import Course
from .serializers import CourseSerializer


class CourseViewSet(viewsets.ModelViewSet):
    # queryset = Course.objects.all().order_by("name")
    serializer_class = CourseSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = Course.objects.all()

        is_enrolled = self.request.GET.get("is_enrolled")
        if is_enrolled is not None:
            student = Student.objects.get(user__id=self.request.user.id)
            if is_enrolled == "true":
                queryset = queryset.filter(group__enrolment__student=student)
            elif is_enrolled == "false":
                queryset = queryset.exclude(group__enrolment__student=student)
            else:
                raise ValidationError(
                    detail="is_enrolled must be either 'true' or 'false'"
                )

        return queryset.order_by("department", "name")


@login_required
def index_courses(request):
    return render(request, "courses/index_courses.html")
