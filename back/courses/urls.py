from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("courses/", views.index_courses, name="courses_index"),
    path("course/<int:course_id>/details", views.view_course, name="course_detail"),
]
