from django.urls import path
from . import views

urlpatterns = [
    path("index_users/", views.index_users),
    path("index_profile/<int:student_id>/", views.index_profile, name="index_profile"),
]
