from django.shortcuts import render
from .models import Student


def index_users(request):
    all_student_list = Student.objects.order_by('-promo__year', 'user__first_name')
    context = {'all_student_list': all_student_list}
    return render(request, 'social/index_users.html', context)
