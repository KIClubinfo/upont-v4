from django.urls import path

from . import views

urlpatterns = [
    path("index_users/", views.index_users),
    path("index_profil/<int:student_id>/", views.index_profil, name="index_profil"),
]
