from django.urls import path

from . import views

app_name = "news"
urlpatterns = [
    path("posts/", views.posts, name="posts"),
    path("events/idex", views.events, name="events"),
    path("event/<int:event_id>/detail", views.event_detail, name="event_detail"),
]
