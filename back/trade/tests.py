from django.test import TestCase

from .models import Transaction


class TransactionModelTest(TestCase):
    fixtures = ["test_trade.json"]

    def balance_change_for_student(self):
        transaction = Transaction.objects.get(pk=1)
        self.assertEqual(-5, transaction.balance_change_for_student)

    def balance_change_for_club(self):
        transaction = Transaction.objects.get(pk=1)
        self.assertEqual(5, transaction.balance_change_for_club)
