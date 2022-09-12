from django.db.models.query import QuerySet
from django.test import TestCase
from django.urls import reverse

from .models import Transaction


class StudentTransactionsViewTest(TestCase):
    fixtures = ["test_trade.json"]

    def test_authenticated_user(self):
        self.client.login(username="test_user", password="azertyuiop123456789!")
        response = self.client.get(reverse("pochtron:trade:student_transactions"))
        self.assertEqual(type(response.context["transactions"]), QuerySet)
        self.assertEqual(len(response.context["transactions"]), 1)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trade/student_transactions.html")
        self.client.logout()


class TransactionModelTest(TestCase):
    fixtures = ["test_trade.json"]

    def balance_change_for_student(self):
        transaction = Transaction.objects.get(pk=1)
        self.assertEqual(-5, transaction.balance_change_for_student)

    def balance_change_for_club(self):
        transaction = Transaction.objects.get(pk=1)
        self.assertEqual(5, transaction.balance_change_for_club)
