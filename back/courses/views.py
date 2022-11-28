from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models.functions import Greatest
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course


@login_required
def view_course(request, course):
    course = get_object_or_404(Course, pk=course_id)
    context = {
        "couse": course,
    }
    return render(request, "courses/view_course.html", context)