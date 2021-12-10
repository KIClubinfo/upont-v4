from django.shortcuts import render
<<<<<<< HEAD
from .models import Student


def index_users(request):
    all_student_list = Student.objects.order_by('-promo__year', 'user__first_name')
    context = {'all_student_list': all_student_list}
    return render(request, 'social/index_users.html', context)

def index_profile(request):
    return render(request, 'social/index_profile.html')
=======

# Create your views here.
>>>>>>> e00915f388ec79b9934fde3585c008937537fddc
