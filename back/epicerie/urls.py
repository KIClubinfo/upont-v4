from django.urls import path

from . import views

app_name = "epicerie"
urlpatterns = [
    path("", views.home, name="home"),
    path("panier/", views.basket, name="panier"),
    path("vrac/", views.vrac, name="vrac"),
    path("recettes/", views.recipes, name="recettes"),
    path("admin/", views.admin, name="admin"),
    path("admin/uploadVrac/", views.uploadVrac, name="upload_vrac"),
    path("admin/uploadBasket/", views.uploadBasket, name="upload_basket"),
]
