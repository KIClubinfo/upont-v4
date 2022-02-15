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
from news.views import PostViewSet
from rest_framework import routers
from social.views import StudentViewSet

from . import views

# ---- API URLS ----#

router = routers.DefaultRouter()
router.register(r"students", StudentViewSet)
router.register(r"posts", PostViewSet)

# ---- OTHER URLS ----#

urlpatterns = [
    path("social/", include("social.urls")),
    path("news/", include("news.urls")),
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
    path("api/", include(router.urls)),
]

if settings.DEBUG:  # in debug anyone can access any image
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns.append(path("media/<path:path>", views.media))
