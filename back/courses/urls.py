from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [path("courses/", views.index_courses, name="courses_index")]
