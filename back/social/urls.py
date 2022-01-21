from django.urls import path

from . import views

app_name = "social"
urlpatterns = [
    path("profile/", views.index_users, name="index_users"),
    path("profile/details", views.profile, name="profile"),
    path("profile/<int:user_id>/details", views.profile, name="profile_viewed"),
    path("search", views.search, name="search"),
    path("profile/edit", views.profile_edit, name="profile_edit"),
    path("club/", views.index_clubs, name="club_index"),
    path("club/<int:club_id>/details", views.view_club, name="club_detail"),
    path("club/<int:club_id>/edit", views.club_edit, name="club_edit"),
]
