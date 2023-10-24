from colocaponts.models import Room, Apartment
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from social.models import Membership, Student
from .forms import EditColoc

# Create your views here.


@login_required
def coloc(request):
    apart_list = Apartment.objects.all()
    context = {"apartment_list": apart_list}
    if request.method == "GET":
        return render(request, "colocaponts/liste_coloc.html", context)


@login_required
def add_coloc(request):
    context = {}
    if request.method == "POST":
        if "Valider" in request.POST:
            form = EditColoc(
                request.user.id,
                request.POST,
                request.FILES,
            )
            if form.is_valid():
                post = form.save(commit=False)
                post.author = Student.objects.get(user__id=request.user.id)
                post.date = timezone.now()
                post.save()
                return HttpResponseRedirect(request.session["origin"])
    else:
        form = EditColoc(
            request.user.id,
        )
    request.session["origin"] = request.META.get("HTTP_REFERER", "colocaponts")
    context["EditPost"] = form
    context["Edit"] = False
    return render(request, "colocaponts/coloc_edit.html", context)
