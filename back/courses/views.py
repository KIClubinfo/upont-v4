from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import viewsets

from .models import Course
from .serializers import CourseSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by("name")
    serializer_class = CourseSerializer
    http_method_names = ["get"]


@login_required
def index_courses(request):
    return render(request, "courses/index_courses.html")
