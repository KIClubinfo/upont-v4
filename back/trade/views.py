from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from social.models import Club, Student

from .models import Transaction


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
