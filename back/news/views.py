from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from social.models import Membership, Student

from .forms import AddShotgun
from .models import Participation, Shotgun


@login_required()
def shotguns(request):
    # shotguns to which the user participated :
    student = get_object_or_404(Student, user__id=request.user.id)
    user_participations = Participation.objects.filter(participant=student)
    user_shotguns = []
    for participation in user_participations:
        user_shotguns.append(participation.shotgun)
    has_user_shotguns = not len(user_participations) == 0
    # shotguns that are not ended and to which the user did not participate :
    next_shotguns = Shotgun.objects.filter(ending_date__gte=timezone.now()).order_by(
        "starting_date"
    )
    for user_shotgun in user_shotguns:
        next_shotguns = next_shotguns.exclude(id=user_shotgun.pk)
    has_next_shotguns = not len(next_shotguns) == 0
    # shotguns that are ended and to which the user did not participate :
    old_shotguns = Shotgun.objects.filter(ending_date__lte=timezone.now()).order_by(
        "ending_date"
    )
    for user_shotgun in user_shotguns:
        old_shotguns = old_shotguns.exclude(id=user_shotgun.pk)
    has_old_shotguns = not len(old_shotguns) == 0

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
    student = get_object_or_404(Student, user__id=request.user.id)
    already_participated = shotgun.participated(student)
    got_accepted = shotgun.got_accepted(student)
    participation = Participation.objects.filter(participant=student, shotgun=shotgun)
    if len(participation) > 0:
        motivation = participation[0].motivation
    else:
        motivation = ""
    context = {
        "shotgun": shotgun,
        "already_participated": already_participated,
        "got_accepted": got_accepted,
        "motivation": motivation,
        "student_is_admin": shotgun.club.is_admin(student.id),
    }
    return render(request, "news/shotgun_detail.html", context)


@login_required()
def shotgun_participate(request, shotgun_id):
    shotgun = get_object_or_404(Shotgun, pk=shotgun_id)
    student = get_object_or_404(Student, user__id=request.user.id)
    if shotgun.participated(student):
        return HttpResponseRedirect(reverse("shotgun_detail", args=(shotgun_id,)))
    if shotgun.requires_motivation:
        try:
            motivation = request.POST["motivation"]
        except (KeyError):
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
            participant=student,
            motivation=motivation,
        )
        participation.save()
    else:
        participation = Participation(
            shotgun=shotgun,
            shotgun_date=timezone.now(),
            participant=student,
        )
        participation.save()
    return HttpResponseRedirect(reverse("shotgun_detail", args=(shotgun_id,)))


@login_required()
def shotguns_admin(request):
    student = get_object_or_404(Student, user__id=request.user.id)
    clubs_admin_memberships = Membership.objects.filter(
        student__pk=student.id, is_admin=True
    )
    clubs_and_shotguns = []
    for club_membership in clubs_admin_memberships:
        club_shotguns = Shotgun.objects.filter(club=club_membership.club)
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
    student = get_object_or_404(Student, user__id=request.user.id)
    if not shotgun.club.is_admin(student.id):
        raise PermissionDenied()
    context = {
        "shotgun": shotgun,
    }
    return render(request, "news/shotguns_admin_detail.html", context)


@login_required()
def fail_participation(request, participation_id):
    participation = get_object_or_404(Participation, pk=participation_id)
    student = get_object_or_404(Student, user__id=request.user.id)
    if not participation.shotgun.club.is_admin(student.id):
        raise PermissionDenied()
    participation.failed_motivation = True
    participation.save()
    return HttpResponseRedirect(
        reverse("shotguns_admin_detail", args=(participation.shotgun.id,))
    )


@login_required()
def unfail_participation(request, participation_id):
    participation = get_object_or_404(Participation, pk=participation_id)
    student = get_object_or_404(Student, user__id=request.user.id)
    if not participation.shotgun.club.is_admin(student.id):
        raise PermissionDenied()
    participation.failed_motivation = False
    participation.save()
    return HttpResponseRedirect(
        reverse("shotguns_admin_detail", args=(participation.shotgun.id,))
    )


@login_required()
def new_shotgun(request):
    student = get_object_or_404(Student, user__id=request.user.id)
    clubs_memberships = Membership.objects.filter(student__pk=student.id, is_admin=True)
    clubs = []
    for membership in clubs_memberships:
        clubs.append(membership.club)

    if request.method == "GET":
        form = AddShotgun(clubs)
        context = {
            "clubs": clubs,
            "has_clubs_admins": len(clubs) > 0,
            "form": form,
        }
        return render(request, "news/shotgun_new.html", context)

    if request.method == "POST":
        form = AddShotgun(
            clubs,
            request.POST,
            request.FILES,
        )
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("shotguns"))


@login_required()
def delete_shotgun(request, shotgun_id):
    student = get_object_or_404(Student, user__id=request.user.id)
    shotgun = get_object_or_404(Shotgun, pk=shotgun_id)
    if not shotgun.club.is_admin(student.id):
        raise PermissionDenied()

    if request.method == "GET":
        context = {
            "shotgun": shotgun,
        }
        return render(request, "news/shotgun_delete.html", context)

    if request.method == "POST":
        shotgun.delete()
        return HttpResponseRedirect(reverse("shotguns_admin"))


@login_required()
def edit_shotgun(request, shotgun_id):
    student = get_object_or_404(Student, user__id=request.user.id)
    shotgun = get_object_or_404(Shotgun, pk=shotgun_id)
    if shotgun.club.is_admin(student.id):
        if request.method == "GET":
            form = AddShotgun([shotgun.club])
            form.fields["title"].initial = shotgun.title
            form.fields["content"].initial = shotgun.content
            form.fields["starting_date"].initial = shotgun.starting_date
            form.fields["ending_date"].initial = shotgun.ending_date
            form.fields["size"].initial = shotgun.size
            form.fields["requires_motivation"].initial = shotgun.requires_motivation
            context = {
                "shotgun": shotgun,
                "form": form,
            }
            return render(request, "news/shotgun_edit.html", context)

        if request.method == "POST":
            form = AddShotgun(
                [shotgun.club], request.POST, request.FILES, instance=shotgun
            )
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(
                    reverse("shotguns_admin_detail", args=(shotgun.id,))
                )
    else:
        raise PermissionDenied()


@login_required()
def publish_shotgun_results(request, shotgun_id):
    student = get_object_or_404(Student, user__id=request.user.id)
    shotgun = get_object_or_404(Shotgun, pk=shotgun_id)
    if shotgun.club.is_admin(student.id):
        shotgun.motivations_review_finished = True
        shotgun.save()
        return HttpResponseRedirect(
            reverse("shotguns_admin_detail", args=(shotgun.id,))
        )
    else:
        raise PermissionDenied()
