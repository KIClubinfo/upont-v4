from django.urls import path

from . import views

app_name = "news"
urlpatterns = [
    path("post/", views.posts, name="posts"),
    path("event/index", views.events, name="events"),
    path("event/<int:event_id>/detail", views.event_detail, name="event_detail"),
    path("event/<int:event_id>/edit", views.event_edit, name="event_edit"),
    path("event/create", views.event_create, name="event_create"),
    path("post/<int:post_id>/edit", views.post_edit, name="post_edit"),
    path("post/create", views.post_create, name="post_create"),
    path("post/<int:post_id>/<str:action>", views.post_like, name="post_like"),
]
