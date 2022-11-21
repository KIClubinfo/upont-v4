from django.urls import path

from . import views

app_name = "the_calendar"

urlpatterns = [
    path("calendar/", views.view_calendar, name="big_calendar"),
]
