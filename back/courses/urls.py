app_name = "course"

from django.urls import path

from . import views


urlpatterns = [
       path("course/<int:course_id>/details", views.view_course, name="course_detail"),
]
