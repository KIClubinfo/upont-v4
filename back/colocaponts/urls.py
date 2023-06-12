from django.urls import path

from . import views

app_name = "colocaponts"

urlpatterns = [
    path("", views.coloc, name="coloc"),
    path("add/", views.add_coloc, name="add_coloc"),

]