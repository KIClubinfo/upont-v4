from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index_courses(request):
    return render(request, "courses/index_courses.html")
