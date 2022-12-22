from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import views, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from social.models import Student

from .models import Course, CourseDepartment
from .serializers import CourseSerializer


class ListCourseDepartments(views.APIView):
    """
    View to list all the department a course can belong to
    """

    def get(self, request):
        return Response(CourseDepartment.values)


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

        departments = self.request.GET.get("department")
        if departments is not None:
            queryset = queryset.filter(department__in=departments.split(","))

        return queryset.order_by("department", "name")


@login_required
def index_courses(request):
    return render(request, "courses/index_courses.html")
