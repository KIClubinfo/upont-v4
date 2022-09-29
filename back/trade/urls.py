from django.urls import path

from . import views

app_name = "trade"

urlpatterns = [
    path("transactions/", views.student_transactions, name="student_transactions"),
    path(
        "transactions/club/<int:club_id>/",
        views.club_transactions,
        name="club_transactions",
    ),
]
