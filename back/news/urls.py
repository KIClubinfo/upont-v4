from django.urls import path

from . import views

urlpatterns = [
    path("shotguns/", views.shotguns, name="shotguns"),
    path("shotguns/<int:shotgun_id>/", views.shotgun_detail, name="shotgun_detail"),
    path(
        "shotguns/<int:shotgun_id>/participate/",
        views.shotgun_participate,
        name="shotgun_participate",
    ),
    path("shotguns/new/", views.new_shotgun, name="new_shotgun"),
    path("shotguns/delete/", views.delete_shotgun, name="delete_shotgun"),
    path(
        "shotguns/delete/<int:shotgun_id>/",
        views.delete_shotgun_detail,
        name="delete_shotgun_detail",
    ),
]
