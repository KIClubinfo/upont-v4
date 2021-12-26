from django.urls import path

from . import views

app_name = "social"
urlpatterns = [
    path("index_users/", views.index_users, name="index_users"),
    path("index_profile/", views.index_profile, name="index_profile"),
    path("index_profile/<int:student_id>/", views.index_profile, name="profile"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("index_clubs/", views.index_clubs, name="club_index"),
    path("view_club/<int:club_id>", views.view_club, name="club_detail"),
]
