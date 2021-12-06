from django.urls import path
from . import views


app_name = 'news'
urlpatterns = [
    path("posts/", views.posts),
    path("events/", views.events, name='events'),
    path("event_detail/<int:event_id>", views.event_detail, name='event_detail'),
]
