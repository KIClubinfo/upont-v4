from django.urls import path

from . import views

app_name = "course"

urlpatterns = [
    path("", views.test_to_delete, name="test"),
]
