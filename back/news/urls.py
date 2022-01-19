from django.urls import path

from . import views

app_name = "news"

urlpatterns = [
    path("post/", views.posts, name="posts"),
    path("event/index", views.events, name="events"),
    path("event/<int:event_id>/detail", views.event_detail, name="event_detail"),
    path("event/<int:event_id>/edit", views.event_edit, name="event_edit"),
    path("event/create", views.event_create, name="event_create"),
    path("post/<int:post_id>/edit", views.post_edit, name="post_edit"),
    path("post/create", views.post_create, name="post_create"),
    path("post/<int:post_id>/<str:action>", views.post_like, name="post_like"),
    path(
        "comment/<int:comment_id>/<int:post_id>",
        views.comment_delete,
        name="comment_delete",
    ),
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
