from django.urls import path
from . import views

app_name = "social"
urlpatterns = [
    path("index_users/", views.index_users, name="index_users"),
    path("profile/", views.profile, name="profile"),
    path("profile/<int:student_id>/", views.profile, name="profile_viewed"),
    path("search", views.search, name="search"),
    path("profile_edit/", views.profile_edit, name="profile_edit"),
    path("index_clubs/", views.index_clubs, name="club_index"),
    path("view_club/<int:club_id>", views.view_club, name="club_detail"),
    path("club_edit/<int:club_id>", views.club_edit, name="club_edit"),
]
