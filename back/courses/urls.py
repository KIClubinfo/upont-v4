from django.urls import path

from news.views import post_create, post_edit

from . import views

app_name = "courses"

urlpatterns = [
    path("courses/", views.index_courses, name="courses_index"),
    path("course/<int:course_id>/details", views.view_course, name="course_detail"),
    path("update_timeslots/", views.update_timeslots, name="update_timeslots"),
    path("group/<int:group_id>/<str:action>", views.join_group, name="join_group"),
    path("add_course/", views.add, name="add_course"),
    path(
        "course/<int:course_id>/post/create",
        post_create,
        name="course_post_create",
    ),
    path(
        "course/<int:course_id>/post/<int:post_id>/edit",
        post_edit,
        name="course_post_edit",
    ),
]
