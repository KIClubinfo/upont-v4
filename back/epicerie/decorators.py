from functools import wraps
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from social.models import Membership, Club, Student

idEpicerie = 1


def studentIsEpicier(user):
    try:
        clubEpicerie = Club.objects.get(pk=idEpicerie)
    except Club.DoesNotExist:
        return False
    try:
        student = get_object_or_404(Student, user__id=user.id)
        student_membership = Membership.objects.get(student=student, club=clubEpicerie)
        return True
    except Membership.DoesNotExist:
        return False


def epicierOnly():
    def decorator(view):
        @wraps(view)
        def _wrapped_view(request, *args, **kwargs):
            if not studentIsEpicier(request.user):
                return HttpResponse("Tu n'es pas épicier")
            return view(request, *args, **kwargs)

        return _wrapped_view

    return decorator
