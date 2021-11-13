from django.urls import path
from . import views


app_name = 'social'
urlpatterns = [
    path("index_users/", views.index_users),
    path("index_clubs/", views.index_clubs, name='club_index'),
    path("view_club/<int:club_id>", views.view_club, name='club_detail'),
]