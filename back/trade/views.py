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

from .forms import AddTransaction
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
                return JsonResponse({"error": ""}, status=201)
            else:
                return JsonResponse({"error": "Pas assez d'argent sur ce compte."})
        return HttpResponse(status=105)


class LastTransactions(APIView):
    """
    API endpoint that returns the last 20 transactions of a club.
    """

    def get(self, request):
        if "club" in request.GET and request.GET["club"].strip():
            club_id = request.GET.get("club", None)
            club = Club.objects.get(pk=club_id)
            student = get_object_or_404(Student, user__pk=request.user.id)
            if not club.is_member(student.id):
                raise PermissionDenied

            transactions = Transaction.objects.filter(good__club=club).order_by(
                "-date"
            )[:20]
            serializer = TransactionSerializer(transactions, many=True)
            return Response({"transactions": serializer.data})
        else:
            return HttpResponse(status=500)
