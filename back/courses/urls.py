from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("courses/", views.index_courses, name="courses_index"),
    path("course/<int:course_id>/details", views.view_course, name="course_detail"),
    path("update_timeslots/", views.update_timeslots, name="update_timeslots"),
    path("group/<int:group_id>/<str:action>", views.join_group, name="join_group"),
    path(
        "course/<int:course_id>/post/create",
        views.course_post_create,
        name="course_post_create",
    ),
]
