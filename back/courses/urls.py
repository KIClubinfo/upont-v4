from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("courses/", views.index_courses, name="courses_index"),
    path("update_timeslots/", views.update_timeslots, name="update_timeslots"),
]
