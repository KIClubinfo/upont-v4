from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("panier/", views.basket, name="panier"),
    path("panier/<int:basket_id>/", views.basket_detail, name="panier_detail"),
]