from django.urls import path

from . import views

app_name = "epicerie"
urlpatterns = [
    path("", views.home, name="home"),
    path("panier/", views.basket, name="panier"),
    path("vrac/", views.vrac, name="vrac"),
    path("recettes/", views.recipes, name="recettes"),
]
