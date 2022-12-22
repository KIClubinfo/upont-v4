from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Course


@login_required
def view_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    context = {
        "course": course,
    }
    return render(request, "courses/view_course.html", context)
