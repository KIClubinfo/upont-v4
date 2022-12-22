from django.urls import path

from . import views

app_name = "course"


urlpatterns = [
    path("course/<int:course_id>/details", views.view_course, name="course_detail"),
]
