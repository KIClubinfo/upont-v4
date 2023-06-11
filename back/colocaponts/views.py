
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
# Create your views here.

@login_required
def coloc(request):
    if request.method == "GET":
        return render(request, "colocaponts/liste_coloc.html")
    
