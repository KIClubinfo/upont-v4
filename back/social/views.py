from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EditProfile
from .models import Club, Membership, Student


@login_required(login_url="/login/")
def index_users(request):
    all_student_list = Student.objects.order_by("-promo__year", "user__first_name")
    context = {"all_student_list": all_student_list}
    return render(request, "social/index_users.html", context)


@login_required(login_url="/login/")
def profile(request, student_id=None):
    if student_id is None:
        student_id = request.user.id
    student = get_object_or_404(Student, pk=student_id)
    membership_club_list = Membership.objects.filter(student__pk=student_id)
    context = {"student": student, "membership_club_list": membership_club_list}
    if student_id == request.user.id:
        return render(request, "social/profile.html", context)
    else:
        return render(request, "social/profile_viewed.html", context)


@login_required(login_url="/login/")
def profile_edit(request):
    student_id = request.user.id
    student = get_object_or_404(Student, pk=student_id)
    membership_club_list = Membership.objects.filter(student__pk=student_id)
    context = {"student": student, "membership_club_list": membership_club_list}

    if request.method == "POST":
        form = EditProfile(
            request.POST, request.FILES, instance=Student.objects.get(user=request.user)
        )
        if form.is_valid():
            if "picture" in request.FILES:
                student.picture.delete()
            form.save()
            return redirect("/social/profile")

    else:
        form = EditProfile()
        form.fields["phone_number"].initial = student.phone_number
        form.fields["department"].initial = student.department
        context["EditProfile"] = form
    return render(request, "social/profile_edit.html", context)


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
