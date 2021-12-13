from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import Membership, Student


@login_required(login_url="/login/")
def index_users(request):
    all_student_list = Student.objects.order_by("-promo__year", "user__first_name")
    context = {"all_student_list": all_student_list}
    return render(request, "social/index_users.html", context)


@login_required(login_url="/login/")
def index_profile(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    membership_club_list = Membership.objects.filter(student__pk=student_id)
    context = {"student": student, "membership_club_list": membership_club_list}
    return render(request, "social/index_profile.html", context)
