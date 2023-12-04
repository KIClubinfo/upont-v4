from django.urls import path

from . import views

app_name = "epicerie"
urlpatterns = [
    path("", views.home, name="home"),
    path("panier/", views.basket, name="panier"),
    path("panier/<int:basket_id>/", views.basket_detail, name="panier_detail"),
    path("commande_panier/", views.basket_order, name="commande_panier"),
    path("vrac/", views.vrac, name="vrac"),
    path("vrac/<int:vrac_id>/", views.vrac_detail, name="vrac_detail"),
    path("commande_vrac/", views.vrac_order, name="commande_vrac"),
    path("recettes/", views.recipes, name="recettes"),
]
