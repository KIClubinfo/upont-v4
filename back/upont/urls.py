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
from courses.views import (
    CourseViewSet,
    GroupViewSet,
    ListCourseDepartments,
    ResourceViewSet,
    TimeslotViewSet,
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django_reverse_js.views import urls_js
from news.views import (
    DeleteCommentView,
    EventViewSet,
    PostCommentView,
    PostCreateView,
    PostCreateViewV2,
    PostDeleteView,
    PostEditView,
    PostReactionView,
    PostViewSet,
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
from rest_framework import routers
from social.views import (
    ClubsViewSet,
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
    StudentViewSet,
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
router.register(r"students", StudentViewSet)
router.register(r"posts", PostViewSet, basename="post")
router.register(r"events", EventViewSet, basename="event")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"groups", GroupViewSet, basename="group")
router.register(r"timeslots", TimeslotViewSet, basename="timeslot")
router.register(r"resources", ResourceViewSet, basename="resource")
router.register(r"clubs", ClubsViewSet)

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
    path("api/id/pochtron/", PochtronId.as_view(), name="pochtron_id"),
    path(
        "api/course_departments/",
        ListCourseDepartments.as_view(),
        name="course_department_list",
    ),
    path("api/calendar_data/", CalendarData.as_view(), name="calendar_data"),
    path("api/get_token/", views.get_token, name="get_token"),
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
    path("api/edit_post/", PostEditView.as_view(), name="post_edit"),
    path("api/student/", OneStudentView.as_view(), name="student"),
    path("api/membership/", StudentMembershipView.as_view(), name="membership"),
    path("api/club/", OneClubView.as_view(), name="club"),
    path("api/media/<path:path>", views.get_media_path, name="get_media_path"),
    path("api/pochtron/balance", PochtronBalance.as_view(), name="pochtron_balance"),
    path(
        "api/pochtron/transactions",
        PochtronTransactions.as_view(),
        name="pochtron_transactions",
    ),
    path("api/pochtron/cagnotte_url/", CagnotteURL.as_view(), name="cagnotte_url"),
    path("api/test/", ProfilePicUpdate.as_view(), name="test"),
]
