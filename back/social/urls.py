from django.urls import path
from . import views

urlpatterns = [
    path("index_users/", views.index_users),
    path("index_clubs/", views.index_clubs),
]