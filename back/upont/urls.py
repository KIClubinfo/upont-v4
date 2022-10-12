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
from news.views import PostViewSet
from pochtron.views import PochtronId, SearchAlcohol
from social.views import (
    CurrentStudentView,
    SearchRole,
    SearchStudent,
    StudentCanPublishAs,
    StudentViewSet,
)
from trade.views import LastTransactions, add_transaction, credit_account

from . import views

# ---- MAIN URLS ----#

urlpatterns = [
    path("social/", include("social.urls")),
    path("news/", include("news.urls")),
    path("pochtron/", include("pochtron.urls")),
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
]

if settings.DEBUG:  # in debug anyone can access any image
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns.append(path("media/<path:path>", views.media))

# ---- API URLS ----#

urlpatterns += [
    path(
        "reverse.js", urls_js, name="reverse_js"
    ),  # for reversing django urls in JavaScript
    path("api/students/", StudentViewSet.as_view({"get": "list"}), name="students"),
    path("api/posts/", PostViewSet.as_view({"get": "list"}), name="posts"),
    path(
        "api/posts/<int:pk>/",
        PostViewSet.as_view({"get": "retrieve"}),
        name="post_detail",
    ),
    path("api/current/", CurrentStudentView.as_view(), name="current_student"),
    path(
        "api/transactions/last/", LastTransactions.as_view(), name="last_transactions"
    ),
    path("api/forms/publish/", StudentCanPublishAs.as_view(), name="publish_comment"),
    path("api/forms/transactions/add/", add_transaction, name="add_transaction"),
    path("api/forms/transactions/credit/", credit_account, name="credit_account"),
    path("api/search/roles/", SearchRole.as_view(), name="search_roles"),
    path("api/search/students/", SearchStudent.as_view(), name="search_students"),
    path("api/search/alcohols/", SearchAlcohol.as_view(), name="search_alcohols"),
    path("api/id/pochtron/", PochtronId.as_view(), name="pochtron_id"),
]
