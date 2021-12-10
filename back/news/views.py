from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from social.models import Student

from .models import Participation, Shotgun


@login_required(login_url="/login/")
def shotguns(request):
    next_shotguns = Shotgun.objects.filter(ending_date__gte=timezone.now()).order_by(
        "starting_date"
    )
    if len(next_shotguns) == 0:
        has_next_shotguns = False
    else:
        has_next_shotguns = True
    old_shotguns = Shotgun.objects.filter(ending_date__lte=timezone.now()).order_by(
        "ending_date"
    )
    if len(old_shotguns) == 0:
        has_old_shotguns = False
    else:
        has_old_shotguns = True
    user_shotguns = Shotgun.objects.filter(
        participations__participant__id__in=[
            Student.objects.get(user__id=request.user.id).id
        ]
    )
    if len(user_shotguns) == 0:
        has_user_shotguns = False
    else:
        has_user_shotguns = True
    context = {
        "next_shotguns": next_shotguns,
        "has_next_shotguns": has_next_shotguns,
        "old_shotguns": old_shotguns,
        "has_old_shotguns": has_old_shotguns,
        "user_shotguns": user_shotguns,
        "has_user_shotguns": has_user_shotguns,
    }
    return render(request, "news/shotguns.html", context)


@login_required(login_url="/login/")
def shotgun_detail(request, shotgun_id):
    shotgun = get_object_or_404(Shotgun, pk=shotgun_id)
    student = Student.objects.get(user__id=request.user.id)
    already_participated = shotgun.participated(student)
    got_accepted = shotgun.got_accepted(student)
    context = {
        "shotgun": shotgun,
        "already_participated": already_participated,
        "got_accepted": got_accepted,
    }
    return render(request, "news/shotgun_detail.html", context)


@login_required(login_url="/login/")
def shotgun_participate(request, shotgun_id):
    shotgun = get_object_or_404(Shotgun, pk=shotgun_id)
    student = Student.objects.get(user__id=request.user.id)
    if shotgun.participated(student):
        return HttpResponseRedirect(reverse("shotgun_detail", args=(shotgun_id,)))
    if shotgun.requires_motivation:
        try:
            motivation = request.POST["motivation"]
        except (KeyError, Motivation.DoesNotExist):
            error_message = "Tu n'as pas fourni de motivation !"
            return HttpResponseRedirect(
                reverse(
                    "shotgun_detail",
                    args=(
                        shotgun_id,
                        error_message,
                    ),
                )
            )
        participation = Participation(
            shotgun_date=timezone.now(),
            participant=Student.objects.get(user__id=request.user.id),
            motivation=motivation,
        )
        participation.save()
        shotgun.participations.add(participation)
    else:
        participation = Participation(
            shotgun_date=timezone.now(),
            participant=Student.objects.get(user__id=request.user.id),
        )
        participation.save()
        shotgun.participations.add(participation)
    return HttpResponseRedirect(reverse("shotgun_detail", args=(shotgun_id,)))


def new_shotgun(request):
    return render(request, "news/shotguns.html")


def delete_shotgun(request):
    return render(request, "news/shotguns.html")


def delete_shotgun_detail(request):
    return render(request, "news/shotguns.html")
