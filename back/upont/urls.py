"""upont URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import django_cas_ng.views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django_reverse_js.views import urls_js
from rest_framework import routers

from courses.views import (
    CourseViewSet,
    GroupViewSet,
    ListCourseDepartments,
    ResourceViewSet,
    TimeslotViewSet,
)
from news.views import (
    DeleteCommentView,
    EventViewSet,
    PartnershipViewSet,
    PostCommentView,
    PostCreateView,
    PostCreateViewV2,
    ShotgunCreateView,
    PostDeleteView,
    PostEditView,
    PostReactionView,
    PostViewSet,
    SearchPost,
    ShotgunParticipateView,
    ShotgunView,
)
from pochtron.views import (
    CagnotteURL,
    PochtronBalance,
    PochtronId,
    PochtronTransactions,
    SearchAlcohol,
)

# Replace MediatekViewSet with LocalViewSet
from services.views import (
    BikesViewSet,
    LocalViewSet,
    OrderViewSet,
    RequestFormViewSet,
    ReservationBikeViewSet,
    ReservationMusicRoomViewSet,
    VracViewSet,
)
from social.views import (
    DeleteAllChannelMessagesView,
    DeleteChannelMessageView,
    DeleteChannelView,
    MessageReactionView,
    MessagePollVoteView,
    CreatePollMessageView,
    RenameChannelView,
    ChannelListView,
    ChannelEncryptedKeyView,
    ChannelJoinRequestCreateView,
    ChannelJoinRequestListView,
    ChannelJoinRequestAcceptView,
    ChannelLeaveView,
    ChannelMembersView,
    ChannelAddMemberView,
    ChannelRemoveMemberView,
    ChannelMessagesView,
    ClubsViewSet,
    CreateChannel,
    CreateMessage,
    CurrentStudentView,
    NotificationTokenView,
    OneClubView,
    OneStudentView,
    ProfilePicUpdate,
    SearchClub,
    SearchRole,
    SearchStudent,
    StudentCanPublishAs,
    StudentMembershipView,
    StudentPublicKeyView,
    StudentPublicKeyByUserView,
    StudentProfileEdit,
    StudentViewSet,
    validate_student,
)
from the_calendar.views import CalendarData
from trade.views import LastTransactions, add_transaction, credit_account

from . import views

# ---- MAIN URLS ----#

urlpatterns = [
    path("social/", include("social.urls")),
    path("news/", include("news.urls")),
    path("pochtron/", include("pochtron.urls")),
    path("courses/", include("courses.urls")),
    path("the_calendar/", include("the_calendar.urls")),
    path("admin/", admin.site.urls),
    path("tellme/", include("tellme.urls"), name="tellme"),
    path("add_promo/", views.add, name="add_promo"),
    path(
        "login/",
        auth_views.LoginView.as_view(redirect_authenticated_user=True),
        name="login",
    ),  # forces redirection of already authenticated users
    path("", include("django.contrib.auth.urls")),
    path("", views.root_redirect),
    path("internal/auth-check/", views.auth_check, name="internal_auth_check"),
    path("cas/login", django_cas_ng.views.LoginView.as_view(), name="cas_ng_login"),
    path("cas/logout", django_cas_ng.views.LogoutView.as_view(), name="cas_ng_logout"),
    path("page_not_created/", views.page_not_created, name="page_not_created"),
    path("privacy", views.privacy, name="privacy"),
    path("contact", views.contact, name="contact"),
]

if settings.DEBUG:  # in debug anyone can access any image
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns.append(path("media/<path:path>", views.media))

# ---- API URLS ----#

router = routers.DefaultRouter()
router.register(
    r"admin-status", views.AdminStatusViewSet, basename="check-admin-status"
)
router.register(r"students", StudentViewSet)
router.register(r"posts", PostViewSet, basename="post")
router.register(r"events", EventViewSet, basename="event")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"groups", GroupViewSet, basename="group")
router.register(r"timeslots", TimeslotViewSet, basename="timeslot")
router.register(r"resources", ResourceViewSet, basename="resource")
router.register(r"clubs", ClubsViewSet)
router.register(r"services/bikes", BikesViewSet, basename="bikes")
router.register(r"services/orders", OrderViewSet, basename="order")
router.register(r"services/vrac", VracViewSet, basename="vrac")
router.register(r"services/requests", RequestFormViewSet, basename="requests")
router.register(
    r"services/reservations", ReservationBikeViewSet, basename="reservations"
)
router.register(
    r"services/musicroom", ReservationMusicRoomViewSet, basename="musicroom"
)
router.register(r"services/locals", LocalViewSet, basename="local")

router.register(r"partnerships", PartnershipViewSet, basename="partnership")

urlpatterns += [
    path(
        "reverse.js", urls_js, name="reverse_js"
    ),  # for reversing django urls in JavaScript
    path("api/", include(router.urls)),
    path("api/current/", CurrentStudentView.as_view(), name="current_student"),
    path(
        "api/transactions/last/", LastTransactions.as_view(), name="last_transactions"
    ),
    path("api/forms/publish/", StudentCanPublishAs.as_view(), name="publish_comment"),
    path("api/forms/transactions/add/", add_transaction, name="add_transaction"),
    path("api/forms/transactions/credit/", credit_account, name="credit_account"),
    path("api/search/roles/", SearchRole.as_view(), name="search_roles"),
    path("api/search/students/", SearchStudent.as_view(), name="search_students"),
    path("api/search/clubs/", SearchClub.as_view(), name="search_clubs"),
    path("api/search/alcohols/", SearchAlcohol.as_view(), name="search_alcohols"),
    path("api/search/posts/", SearchPost.as_view(), name="search_posts"),
    path("api/channels/", ChannelListView.as_view(), name="channels_list"),
    path("api/channels/create/", CreateChannel.as_view(), name="create_channel"),
    path(
        "api/channels/<int:channel_id>/join-request/",
        ChannelJoinRequestCreateView.as_view(),
        name="channel_join_request_create",
    ),
    path(
        "api/channels/<int:channel_id>/join-requests/",
        ChannelJoinRequestListView.as_view(),
        name="channel_join_requests_list",
    ),
    path(
        "api/channels/<int:channel_id>/join-requests/<int:join_request_id>/accept/",
        ChannelJoinRequestAcceptView.as_view(),
        name="channel_join_request_accept",
    ),
    path(
        "api/channels/<int:channel_id>/messages/",
        ChannelMessagesView.as_view(),
        name="channel_messages",
    ),
    path(
        "api/channels/<int:channel_id>/key/",
        ChannelEncryptedKeyView.as_view(),
        name="channel_encrypted_key",
    ),
    path("api/messages/create/", CreateMessage.as_view(), name="create_message"),
    path(
        "api/messages/create-poll/",
        CreatePollMessageView.as_view(),
        name="create_poll_message",
    ),
    path(
        "api/channels/<int:channel_id>/delete/",
        DeleteChannelView.as_view(),
        name="delete_channel",
    ),
    path(
        "api/messages/<int:message_id>/delete/",
        DeleteChannelMessageView.as_view(),
        name="delete_channel_message",
    ),
    path(
        "api/messages/<int:message_id>/reaction/",
        MessageReactionView.as_view(),
        name="message_reaction",
    ),
    path(
        "api/messages/<int:message_id>/poll-vote/",
        MessagePollVoteView.as_view(),
        name="message_poll_vote",
    ),
    path(
        "api/channels/<int:channel_id>/messages/delete-all/",
        DeleteAllChannelMessagesView.as_view(),
        name="delete_all_channel_messages",
    ),
    path(
        "api/channels/<int:channel_id>/rename/",
        RenameChannelView.as_view(),
        name="rename_channel",
    ),
    path("api/public-key/", StudentPublicKeyView.as_view(), name="student_public_key"),
    path(
        "api/public-key/<int:user_id>/",
        StudentPublicKeyByUserView.as_view(),
        name="student_public_key_by_user",
    ),
    path(
        "api/channels/<int:channel_id>/members/add/",
        ChannelAddMemberView.as_view(),
        name="channel_add_member",
    ),
    path(
        "api/channels/<int:channel_id>/members/",
        ChannelMembersView.as_view(),
        name="channel_members_list",
    ),
    path(
        "api/channels/<int:channel_id>/members/<int:user_id>/remove/",
        ChannelRemoveMemberView.as_view(),
        name="channel_remove_member",
    ),
    path(
        "api/channels/<int:channel_id>/leave/",
        ChannelLeaveView.as_view(),
        name="channel_leave",
    ),
    path("api/id/pochtron/", PochtronId.as_view(), name="pochtron_id"),
    path(
        "api/course_departments/",
        ListCourseDepartments.as_view(),
        name="course_department_list",
    ),
    path("api/calendar_data/", CalendarData.as_view(), name="calendar_data"),
    path("api/get_token/", views.get_token, name="get_token"),
    path("api/get_sso_token/", views.get_sso_token, name="get_sso_token"),
    path("api/shotguns/", ShotgunView.as_view(), name="shotgun"),
    path(
        "api/shotgun/participate/",
        ShotgunParticipateView.as_view(),
        name="shotgun_participate",
    ),
    path(
        "api/notification_token/", NotificationTokenView.as_view(), name="student_token"
    ),
    path("api/post_reaction/", PostReactionView.as_view(), name="post_reaction"),
    path(
        "api/news/post/delete/", PostDeleteView.as_view(), name="api_news_post_delete"
    ),
    path(
        "api/news/comment/delete/",
        DeleteCommentView.as_view(),
        name="api_news_comment_delete",
    ),
    path("api/comment_post/", PostCommentView.as_view(), name="post_comment"),
    path("api/create_post/", PostCreateView.as_view(), name="post_creation"),
    path("api/create_post/v2/", PostCreateViewV2.as_view(), name="post_creation_v2"),
    path("api/create_shotgun/", ShotgunCreateView.as_view(), name="create_shotgun"),
    path("api/edit_post/", PostEditView.as_view(), name="post_edit"),
    path("api/student/", OneStudentView.as_view(), name="student"),
    path("api/membership/", StudentMembershipView.as_view(), name="membership"),
    path("api/club/", OneClubView.as_view(), name="club"),
    path("api/media/<path:path>", views.get_media_path, name="get_media_path"),
    path("api/pochtron/balance/", PochtronBalance.as_view(), name="pochtron_balance"),
    path(
        "api/pochtron/transactions/",
        PochtronTransactions.as_view(),
        name="pochtron_transactions",
    ),
    path("api/pochtron/cagnotte_url/", CagnotteURL.as_view(), name="cagnotte_url"),
    path("api/test/", ProfilePicUpdate.as_view(), name="test"),
    path("api/edit_profile/", StudentProfileEdit.as_view(), name="edit_profile"),
    path("api/validate-student/", validate_student, name="validate_student"),
]
