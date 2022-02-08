from django.urls import include, path

app_name = "pochtron"

urlpatterns = [
    path("", include("trade.urls")),
]
