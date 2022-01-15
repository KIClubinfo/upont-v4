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
    path(
        "shotguns/<int:shotgun_id>/delete/",
        views.delete_shotgun,
        name="delete_shotgun",
    ),
    path(
        "shotguns/<int:shotgun_id>/edit/",
        views.edit_shotgun,
        name="edit_shotgun",
    ),
    path("shotguns/admin/", views.shotguns_admin, name="shotguns_admin"),
    path(
        "shotguns/<int:shotgun_id>/admin/",
        views.shotguns_admin_detail,
        name="shotguns_admin_detail",
    ),
    path(
        "shotguns/admin/fail/<int:participation_id>",
        views.fail_participation,
        name="fail_participation",
    ),
    path(
        "shotguns/admin/unfail/<int:participation_id>",
        views.unfail_participation,
        name="unfail_participation",
    ),
    path(
        "shotguns/<int:shotgun_id>/admin/publish_shotgun_results/",
        views.publish_shotgun_results,
        name="publish_shotgun_results",
    ),
]
