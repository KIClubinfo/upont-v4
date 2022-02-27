from django.urls import include, path

from . import views

app_name = "pochtron"

urlpatterns = [
    path("", include("trade.urls"), name="trade"),
    path("accounts", views.manage_accounts, name="manage_accounts"),
    path("shop", views.shop, name="shop"),
    path("create_consos", views.create_consos, name="create_consos"),
    path("global_stats", views.global_stats, name="global_stats"),
]
