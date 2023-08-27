from django.urls import path

from . import views

app_name = "news"

urlpatterns = [
    path("post/", views.posts, name="posts"),
    path("page/<slug:page_slug>/", views.page, name="page"),
    path("pages/", views.pages, name="pages"),
    path("event/", views.events, name="events"),
    path("event/<int:event_id>/detail", views.event_detail, name="event_detail"),
    path("event/<int:event_id>/edit", views.event_edit, name="event_edit"),
    path("event/create", views.event_create, name="event_create"),
    path(
        "event/<int:event_id>/<str:action>",
        views.event_participate,
        name="event_participate",
    ),
    path("post/<int:post_id>/edit", views.post_edit, name="post_edit"),
    path("post/create", views.post_create, name="post_create"),
    path(
        "post/create/<int:event_id>", views.post_create, name="post_create_with_origin"
    ),
    path("post/create/<slug:page_slug>", views.post_create_on_page, name="post_create_on_page"),
    path("post/<int:post_id>/<str:action>", views.post_like, name="post_like"),
    path("comment/add/<int:post_id>/", views.comment_post, name="comment_post"),
    path(
        "comment/delete/<int:comment_id>/",
        views.delete_comment,
        name="comment_delete",
    ),
    path("shotgun/", views.shotguns, name="shotguns"),
    path("shotgun/<int:shotgun_id>/", views.shotgun_detail, name="shotgun_detail"),
    path(
        "shotgun/<int:shotgun_id>/participate/",
        views.shotgun_participate,
        name="shotgun_participate",
    ),
    path("shotgun/new/", views.new_shotgun, name="new_shotgun"),
    path(
        "shotgun/<int:shotgun_id>/delete/",
        views.delete_shotgun,
        name="delete_shotgun",
    ),
    path(
        "shotgun/<int:shotgun_id>/edit/",
        views.edit_shotgun,
        name="edit_shotgun",
    ),
    path("shotgun/admin/", views.shotguns_admin, name="shotguns_admin"),
    path(
        "shotgun/<int:shotgun_id>/admin/",
        views.shotguns_admin_detail,
        name="shotguns_admin_detail",
    ),
    path(
        "shotgun/admin/fail/<int:participation_id>",
        views.fail_participation,
        name="fail_participation",
    ),
    path(
        "shotgun/admin/unfail/<int:participation_id>",
        views.unfail_participation,
        name="unfail_participation",
    ),
    path(
        "shotgun/<int:shotgun_id>/admin/publish_shotgun_results/",
        views.publish_shotgun_results,
        name="publish_shotgun_results",
    ),
    path(
        "markdown",
        views.markdown,
        name="markdown",
    ),
]
