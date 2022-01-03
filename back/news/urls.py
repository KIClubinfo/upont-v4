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
        "shotguns/<int:shotgun_id>/delete/",
        views.delete_shotgun_detail,
        name="delete_shotgun_detail",
    ),
    path("shotguns/admin/", views.shotguns_admin, name="shotguns_admin"),
    path(
        "shotguns/<int:shotgun_id>/admin/",
        views.shotguns_admin_detail,
        name="shotguns_admin_detail",
    ),
    path(
        "shotguns/<int:participation_id>/admin/fail/",
        views.fail_participation,
        name="fail_participation",
    ),
]
