from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from social.models import Membership, Student

from .models import Participation, Shotgun


@login_required()
def shotguns(request):
    next_shotguns = Shotgun.objects.filter(ending_date__gte=timezone.now()).order_by(
        "starting_date"
    )
    has_next_shotguns = not len(next_shotguns) == 0
    old_shotguns = Shotgun.objects.filter(ending_date__lte=timezone.now()).order_by(
        "ending_date"
    )
    has_old_shotguns = not len(old_shotguns) == 0
    if request.user.is_superuser:
        has_user_shotguns = False
        user_shotguns = []
    else:
        student = Student.objects.get(user__id=request.user.id)
        user_participations = Participation.objects.filter(participant=student)
        user_shotguns = []
        for participation in user_participations:
            user_shotguns.append(participation.shotgun)
            print(participation.shotgun)
        has_user_shotguns = not len(user_participations) == 0
    context = {
        "next_shotguns": next_shotguns,
        "has_next_shotguns": has_next_shotguns,
        "old_shotguns": old_shotguns,
        "has_old_shotguns": has_old_shotguns,
        "user_shotguns": user_shotguns,
        "has_user_shotguns": has_user_shotguns,
    }
    return render(request, "news/shotguns.html", context)


@login_required()
def shotgun_detail(request, shotgun_id):
    shotgun = get_object_or_404(Shotgun, pk=shotgun_id)
    if request.user.is_superuser:
        already_participated = False
        got_accepted = False
        motivation = ""
    else:
        student = Student.objects.get(user__id=request.user.id)
        already_participated = shotgun.participated(student)
        got_accepted = shotgun.got_accepted(student)
        participation = Participation.objects.filter(
            participant=student, shotgun=shotgun
        )
        if len(participation) > 0:
            motivation = participation[0].motivation
        else:
            motivation = ""
    context = {
        "shotgun": shotgun,
        "already_participated": already_participated,
        "got_accepted": got_accepted,
        "motivation": motivation,
    }
    return render(request, "news/shotgun_detail.html", context)


@login_required()
def shotgun_participate(request, shotgun_id):
    shotgun = get_object_or_404(Shotgun, pk=shotgun_id)
    if request.user.is_superuser:
        return HttpResponseRedirect(reverse("shotgun_detail", args=(shotgun_id,)))
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
            shotgun=shotgun,
            shotgun_date=timezone.now(),
            participant=Student.objects.get(user__id=request.user.id),
            motivation=motivation,
        )
        participation.save()
    else:
        participation = Participation(
            shotgun=shotgun,
            shotgun_date=timezone.now(),
            participant=Student.objects.get(user__id=request.user.id),
        )
        participation.save()
    return HttpResponseRedirect(reverse("shotgun_detail", args=(shotgun_id,)))


@login_required()
def shotguns_admin(request):
    student = Student.objects.get(user__id=request.user.id)
    clubs_memberships = Membership.objects.filter(student__pk=student.id)
    clubs_and_shotguns = []
    for club_membership in clubs_memberships:
        club_shotguns = Shotgun.objects.filter(
            club=club_membership.club, requires_motivation=True
        )
        if len(club_shotguns) > 0:
            clubs_and_shotguns.append(
                {"club": club_membership.club, "shotguns": club_shotguns}
            )
    not_empty = len(clubs_and_shotguns) > 0
    context = {
        "clubs_and_shotguns": clubs_and_shotguns,
        "not_empty": not_empty,
    }
    return render(request, "news/shotguns_admin.html", context)


@login_required()
def shotguns_admin_detail(request, shotgun_id):
    shotgun = get_object_or_404(Shotgun, pk=shotgun_id)
    context = {
        "shotgun": shotgun,
    }
    return render(request, "news/shotguns_admin_detail.html", context)


@login_required()
def fail_participation(request, participation_id):
    participation = get_object_or_404(Participation, pk=participation_id)
    student = Student.objects.get(user__id=request.user.id)
    if not participation.shotgun.club.is_member(student.id):
        return HttpResponseRedirect(reverse("shotguns"))
    participation.failed_motivation = True
    participation.save()
    return HttpResponseRedirect(
        reverse("shotguns_admin_detail", args=(participation.shotgun.id,))
    )


def new_shotgun(request):
    return render(request, "news/shotguns.html")


def delete_shotgun(request):
    return render(request, "news/shotguns.html")


def delete_shotgun_detail(request):
    return render(request, "news/shotguns.html")
