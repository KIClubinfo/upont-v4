from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import Club, Membership, Student


@login_required
def index_users(request):
    all_student_list = Student.objects.order_by("-promo__year", "user__first_name")
    context = {"all_student_list": all_student_list}
    return render(request, "social/index_users.html", context)


@login_required
def index_profile(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    membership_club_list = Membership.objects.filter(student__pk=student_id)
    context = {"student": student, "membership_club_list": membership_club_list}
    return render(request, "social/index_profile.html", context)


@login_required
def index_clubs(request):
    all_clubs_list = Club.objects.order_by("name")
    context = {"all_clubs_list": all_clubs_list}
    return render(request, "social/index_clubs.html", context)


@login_required
def view_club(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    context = {"club": club}
    return render(request, "social/view_club.html", context)
