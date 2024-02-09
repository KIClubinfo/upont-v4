from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "ressource"

router = routers.DefaultRouter()
# router.register(r"logos", LogoViewSet)

urlpatterns = [
    # path("api/", include(router.urls)),
    path(
        "logos/",
        views.view_logoDisplay,
    )  # name="logoDisplay"),
    # Add other URLs as needed
]
