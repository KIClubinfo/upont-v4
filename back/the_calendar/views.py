from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def view_calendar(request):
    return render(request, "calendar/calendar.html")
