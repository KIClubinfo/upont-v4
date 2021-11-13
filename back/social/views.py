from django.shortcuts import render
from .models import Student, Club
from django.contrib.auth.decorators import login_required


@login_required
def index_users(request):
    all_student_list = Student.objects.order_by('-promo__year', 'user__first_name')
    context = {'all_student_list': all_student_list}
    return render(request, 'social/index_users.html', context)


@login_required
def index_profile(request):
    return render(request, 'social/index_profile.html')


def index_clubs(request):
    all_clubs_list = Club.objects.order_by('name')
    context = {'all_clubs_list': all_clubs_list}
    return render(request, 'social/index_clubs.html', context)
