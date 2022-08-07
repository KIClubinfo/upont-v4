import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from social.models import Club, Student
from trade.serializers import TransactionSerializer

from .forms import AddTransaction, EditGood, EditPrice
from .models import Good, Transaction


@login_required
def student_transactions(request):
    student = get_object_or_404(Student, user__id=request.user.id)
    transactions = Transaction.objects.filter(student=student).order_by("-date")
    context = {
        "transactions": transactions,
        "student": student,
    }
    return render(request, "trade/student_transactions.html", context)


@login_required
def club_transactions(request, club_id):
    student = get_object_or_404(Student, user__id=request.user.id)
    club = get_object_or_404(Club, pk=club_id)
    if not club.is_member(student.id):
        raise PermissionDenied
    transactions = Transaction.objects.filter(good__club=club).order_by("-date")
    context = {
        "transactions": transactions,
        "club": club,
    }
    return render(request, "trade/club_transactions.html", context)


@login_required
def add_transaction(request):
    student = get_object_or_404(Student, user__pk=request.user.id)
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        good = get_object_or_404(Good, pk=data["good"])
        if not good.club.is_member(student.id):
            raise PermissionDenied

        filled_form = AddTransaction(
            {
                "good": data["good"],
                "student": data["student"],
                "quantity": 1,
                "date": timezone.now(),
            },
        )
        if filled_form.is_valid():
            all_transactions_with_this_club = Transaction.objects.filter(
                good__club=good.club, student__pk=data["student"]
            )
            balance = 0
            for transaction in all_transactions_with_this_club:
                balance += (
                    transaction.quantity * transaction.balance_change_for_student()
                )
            balance -= good.price()
            if balance >= 0:
                filled_form.save()
                return JsonResponse({"error": "", "new_balance": balance}, status=201)
            else:
                return JsonResponse(
                    {
                        "error": "Pas assez d'argent sur ce compte.\
                     Solde actuel : {} €".format(
                            (balance + good.price()) / 100
                        )
                    }
                )
        return JsonResponse(
            {"error": "Merci de remplir le formulaire correctement."}, status=500
        )


class LastTransactions(APIView):
    """
    API endpoint that returns the last transactions of a club.
    """

    def get(self, request):
        if "club" in request.GET and request.GET["club"].strip():
            club_id = request.GET.get("club", None)
            club = Club.objects.get(pk=club_id)
            student = get_object_or_404(Student, user__pk=request.user.id)
            if not club.is_member(student.id):
                raise PermissionDenied
            if "end" in request.GET and request.GET["end"].strip():
                end = int(request.GET.get("end", 20))
            else:
                end = 20
            if "start" in request.GET and request.GET["start"].strip():
                start = int(request.GET.get("start", 0))
            else:
                start = 0
            transactions = Transaction.objects.filter(good__club=club).order_by("-date")
            serializer = TransactionSerializer(transactions[start:end], many=True)
            has_more = end < len(transactions)
            return Response({"transactions": serializer.data, "has_more": has_more})
        else:
            return HttpResponse(status=500)


@login_required
def credit_account(request):
    student = get_object_or_404(Student, user__pk=request.user.id)
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        club = get_object_or_404(Club, pk=data["club"])
        if not club.is_member(student.id):
            raise PermissionDenied

        good_form = EditGood(
            {
                "name": "Crédit",
                "club": club,
            },
        )
        if good_form.is_valid():
            good = good_form.save()
            price_form = EditPrice(
                {
                    "good": good,
                    "price": -int(data["amount"]),
                    "date": timezone.now(),
                }
            )
            if price_form.is_valid:
                price_form.save()
                transaction_form = AddTransaction(
                    {
                        "student": get_object_or_404(Student, pk=data["student"]),
                        "good": good,
                        "date": timezone.now(),
                        "quantity": 1,
                    }
                )
                if transaction_form.is_valid():
                    transaction_form.save()
                    return JsonResponse({"error": ""}, status=201)
    return JsonResponse(
        {"error": "Merci de remplir le formulaire correctement."}, status=500
    )
