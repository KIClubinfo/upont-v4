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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from upont.add_promo import add

from . import views

urlpatterns = [
    path("social/", include("social.urls")),
    path("admin/", admin.site.urls),
    path("tellme/", include("tellme.urls"), name="tellme"),
    path("add_promo/", add),
    path("", include("django.contrib.auth.urls")),
    path("", views.root_redirect),
]

if settings.DEBUG:  # in debug anyone can access any image
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns.append(path("media/<path:path>", views.media))
