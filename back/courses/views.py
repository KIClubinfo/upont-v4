from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models.functions import Greatest
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course


@login_required
def view_course(request, course):
    course = get_object_or_404(Course, pk=course_id)
    active_members = Membership.objects.filter(club__id=club_id, is_old=False)
    old_members = get_old_members(club_id)
    membership_club_list = Membership.objects.filter(
        student__user__id=request.user.id, club__pk=club_id
    )
    if not membership_club_list:  # If no match is found
        is_admin = False
    elif not membership_club_list[0].is_admin:  # If the user does not have the rights
        is_admin = False
    else:
        is_admin = True
    context = {
        "club": club,
        "active_members": active_members,
        "old_members": old_members,
        "is_admin": is_admin,
    }
    return render(request, "social/view_club.html", context)