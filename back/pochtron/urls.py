from django.urls import include, path

from . import views

app_name = "pochtron"

urlpatterns = [
    path("", include("trade.urls"), name="trade"),
    path("", views.home, name="home"),
    path("admin/", views.admin_home_page, name="admin"),
    path("admin/accounts/", views.manage_accounts, name="manage_accounts"),
    path("admin/shop/", views.shop, name="shop"),
    path("admin/conso/create/", views.conso_create, name="conso_create"),
    path("admin/conso/edit/<int:conso_id>/", views.conso_edit, name="conso_edit"),
    path("admin/manage_admins/", views.manage_admins, name="manage_admins"),
    path(
        "admin/manage_admins/edit/<int:admin_id>", views.admin_edit, name="admin_edit"
    ),
    path("admin/manage_admins/create", views.admin_create, name="admin_create"),
]
