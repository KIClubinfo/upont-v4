import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from social.models import Membership, Student

from .forms import AddShotgun, CommentForm, EditEvent, EditPost
from .models import Comment, Event, Participation, Post, Shotgun
from .serializers import EventSerializer, PostSerializer


@login_required
def posts(request):
    if request.method == "GET":
        return render(request, "news/posts.html")

    elif request.method == "POST":
        student = get_object_or_404(Student, user__id=request.user.id)
        data = json.loads(request.body.decode("utf-8"))
        commented_post_id = data["post"]
        commented_post = get_object_or_404(Post, id=commented_post_id)
        filled_form = CommentForm(commented_post_id, student.user.id, data=data)

        if filled_form.is_valid():
            new_comment = filled_form.save(commit=False)
            new_comment.post = commented_post
            new_comment.author = student
            new_comment.date = timezone.now()
            new_comment.save()
            return HttpResponse(status=201)
        return HttpResponse(status=500)


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows posts to be viewed.
    """

    queryset = Post.objects.filter(course__isnull=True).order_by("-date", "title")
    serializer_class = PostSerializer
    http_method_names = ["get"]


class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows events to be viewed

    Args:

      * "is_enrolled" = true|false

            - if true, return only the timeslots associated with courses in
              which the current user is enrolled

            - if false, return only the timeslots associated with courses in
              which the current user is not enrolled

            - by default, return all timeslots

      * "start" = date is ISO format

            - if given, return only the timeslots which start or end after the
              given date

      * "end" = date is ISO format

            - if given, return only the timeslots which start or end before the
              given date
    """

    serializer_class = EventSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = Event.objects.all()

        start = self.request.GET.get("start")
        if start is not None:
            start_datetime = parse_datetime(start)
            if start_datetime is not None:
                queryset = queryset.filter(
                    Q(date__gte=start_datetime) | Q(end__gte=start_datetime)
                )
            else:
                raise ValidationError(
                    detail="Error in parsing start parameter, the date must be in ISO format"
                )

        end = self.request.GET.get("end")
        if end is not None:
            end_datetime = parse_datetime(end)
            if end_datetime is not None:
                queryset = queryset.filter(
                    Q(date__lte=end_datetime) | Q(end__lte=end_datetime)
                )
            else:
                raise ValidationError(
                    detail="Error in parsing end parameter, the date must be in ISO format"
                )

        # Must be the last argument to handle because no filter is alllowed
        # after a queryset difference (case if is_enrolled=false)
        is_enrolled = self.request.GET.get("is_enrolled")
        if is_enrolled is not None:
            student = get_object_or_404(Student, user__id=self.request.user.id)
            if is_enrolled == "true":
                queryset = queryset.intersection(student.events.all())
            elif is_enrolled == "false":
                queryset = queryset.difference(student.events.all())
            else:
                raise ValidationError(
                    detail="is_enrolled must be either 'true' or 'false'"
                )

        return queryset.order_by("-date", "name")


@login_required
def events(request):
    student = get_object_or_404(Student, user__id=request.user.id)
    all_events_list = Event.objects.order_by("-date")
    is_member = Membership.objects.filter(student=student).exists()
    context = {"all_events_list": all_events_list, "is_member": is_member}
    return render(request, "news/events.html", context)


@login_required
def event_detail(request, event_id):
    student = get_object_or_404(Student, user__id=request.user.id)
    event = get_object_or_404(Event, pk=event_id)
    event_posts = Post.objects.filter(event__pk=event_id).order_by("-date")
    is_member = event.club.is_member(student.id)
    context = {
        "event": event,
        "event_posts": event_posts,
        "is_member": is_member,
        "student": student,
    }
    return render(request, "news/event_detail.html", context)


@login_required
def event_edit(request, event_id):
    student = get_object_or_404(Student, user__id=request.user.id)
    event = get_object_or_404(Event, pk=event_id)
    membership_club_list = Membership.objects.filter(
        student__pk=student.id, club__pk=event.club.id
    )
    if not membership_club_list:  # If no match is found
        raise PermissionDenied

    event = get_object_or_404(Event, id=event_id)
    context = {}
    if request.method == "POST":
        if "Supprimer" in request.POST:
            event.delete()
            return redirect("news:events")
        elif "Valider" in request.POST:
            form = EditEvent(
                request.user.id,
                request.POST,
                request.FILES,
                instance=Event.objects.get(id=event_id),
            )
            if form.is_valid():
                if "poster" in request.FILES:
                    event.poster.delete()
                form.save()
                return redirect("news:events")

    else:
        form = EditEvent(request.user.id, instance=event)
    context["EditEvent"] = form
    context["event"] = event
    context["Edit"] = True
    return render(request, "news/event_edit.html", context)


@login_required
def event_create(request):
    context = {}
    if request.method == "POST":
        if "Valider" in request.POST:
            form = EditEvent(
                request.user.id,
                request.POST,
                request.FILES,
            )
            if form.is_valid():
                form.save()
                return redirect("news:events")
    else:
        form = EditEvent(request.user.id)
    context["EditEvent"] = form
    return render(request, "news/event_edit.html", context)


@login_required
def event_participate(request, event_id, action):
    event = get_object_or_404(Event, id=event_id)
    student = get_object_or_404(Student, user__id=request.user.id)
    if action == "Unparticipate":
        event.participants.remove(student)
    elif action == "Participate":
        event.participants.add(student)
    return redirect("news:event_detail", event_id)


@login_required
def post_edit(request, post_id):
    student = get_object_or_404(Student, user__id=request.user.id)
    post = get_object_or_404(Post, id=post_id)

    if post.club:
        if not post.club.is_member(student.id):
            raise PermissionDenied
    else:
        if post.author.user.id != request.user.id:
            raise PermissionDenied

    context = {}
    if request.method == "POST":
        if "Supprimer" in request.POST:
            post.delete()
            return HttpResponseRedirect(request.session["origin"])
        elif "Valider" in request.POST:
            form = EditPost(
                request.user.id,
                request.POST,
                request.FILES,
                instance=Post.objects.get(id=post_id),
            )
            if form.is_valid():
                if "illustration" in request.FILES:
                    post.illustration.delete()
                form.save()
                return HttpResponseRedirect(request.session["origin"])

    else:
        form = EditPost(request.user.id, instance=post)
    context["EditPost"] = form
    context["post"] = post
    context["Edit"] = True
    request.session["origin"] = request.META.get("HTTP_REFERER", "news:posts")
    return render(request, "news/post_edit.html", context)


@login_required
def post_create(request, event_id=None):
    context = {}
    if request.method == "POST":
        if "Valider" in request.POST:
            form = EditPost(
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
        form = EditPost(request.user.id)
        if event_id is not None:
            form.fields["event"].initial = get_object_or_404(Event, id=event_id)
    request.session["origin"] = request.META.get("HTTP_REFERER", "news:posts")
    context["EditPost"] = form
    context["Edit"] = False
    return render(request, "news/post_edit.html", context)


@login_required
def post_like(request, post_id, action):
    post = get_object_or_404(Post, id=post_id)
    student = get_object_or_404(Student, user__id=request.user.id)
    if action == "Unlike":
        post.likes.remove(student)
    elif action == "Like":
        post.likes.add(student)
        post.dislikes.remove(student)
    elif action == "Dislike":
        post.dislikes.add(student)
        post.likes.remove(student)
    elif action == "Undislike":
        post.dislikes.remove(student)
    else:
        return HttpResponse(status=500)
    return HttpResponse(status=200)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    student = get_object_or_404(Student, user__id=request.user.id)
    student_clubs = student.clubs.all()
    if comment.author.pk == student.pk or (comment.club in student_clubs):
        comment.delete()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)


@login_required
def shotguns(request):
    # shotguns to which the user participated :
    student = get_object_or_404(Student, user__id=request.user.id)
    user_participations = Participation.objects.filter(participant=student)
    user_shotguns = []
    for participation in user_participations:
        user_shotguns.append(participation.shotgun)
    # shotguns that are not ended and to which the user did not participate :
    next_shotguns = Shotgun.objects.filter(ending_date__gte=timezone.now()).order_by(
        "starting_date"
    )
    for user_shotgun in user_shotguns:
        next_shotguns = next_shotguns.exclude(id=user_shotgun.pk)
    # shotguns that are ended and to which the user did not participate :
    old_shotguns = Shotgun.objects.filter(ending_date__lte=timezone.now()).order_by(
        "ending_date"
    )
    for user_shotgun in user_shotguns:
        old_shotguns = old_shotguns.exclude(id=user_shotgun.pk)

    # check is user is admin of at least one club :
    display_admin_button = (
        len(Membership.objects.filter(student__pk=student.id, is_admin=True)) > 0
    )

    context = {
        "next_shotguns": next_shotguns,
        "old_shotguns": old_shotguns,
        "user_shotguns": user_shotguns,
        "display_admin_button": display_admin_button,
    }
    return render(request, "news/shotguns.html", context)


@login_required
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


@login_required
def shotgun_participate(request, shotgun_id):
    shotgun = get_object_or_404(Shotgun, pk=shotgun_id)
    student = get_object_or_404(Student, user__id=request.user.id)
    if shotgun.participated(student):
        return HttpResponseRedirect(reverse("news:shotgun_detail", args=(shotgun_id,)))
    if shotgun.requires_motivation:
        try:
            motivation = request.POST["motivation"]
        except KeyError:
            error_message = "Tu n'as pas fourni de motivation !"
            return HttpResponseRedirect(
                reverse(
                    "news:shotgun_detail",
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
    return HttpResponseRedirect(reverse("news:shotgun_detail", args=(shotgun_id,)))


@login_required
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
    context = {
        "clubs_and_shotguns": clubs_and_shotguns,
    }
    return render(request, "news/shotguns_admin.html", context)


@login_required
def shotguns_admin_detail(request, shotgun_id):
    shotgun = get_object_or_404(Shotgun, pk=shotgun_id)
    student = get_object_or_404(Student, user__id=request.user.id)
    if not shotgun.club.is_admin(student.id):
        raise PermissionDenied()
    context = {
        "shotgun": shotgun,
    }
    return render(request, "news/shotguns_admin_detail.html", context)


@login_required
def fail_participation(request, participation_id):
    participation = get_object_or_404(Participation, pk=participation_id)
    student = get_object_or_404(Student, user__id=request.user.id)
    if not participation.shotgun.club.is_admin(student.id):
        raise PermissionDenied()
    participation.failed_motivation = True
    participation.save()
    return HttpResponseRedirect(
        reverse("news:shotguns_admin_detail", args=(participation.shotgun.id,))
    )


@login_required
def unfail_participation(request, participation_id):
    participation = get_object_or_404(Participation, pk=participation_id)
    student = get_object_or_404(Student, user__id=request.user.id)
    if not participation.shotgun.club.is_admin(student.id):
        raise PermissionDenied()
    participation.failed_motivation = False
    participation.save()
    return HttpResponseRedirect(
        reverse("news:shotguns_admin_detail", args=(participation.shotgun.id,))
    )


@login_required
def new_shotgun(request):
    student = get_object_or_404(Student, user__id=request.user.id)
    admin_clubs_memberships = Membership.objects.filter(
        student__pk=student.id, is_admin=True
    )
    clubs = []
    for membership in admin_clubs_memberships:
        clubs.append(membership.club)

    if request.method == "GET":
        form = AddShotgun(clubs)
        context = {
            "has_clubs_admins": len(clubs) > 0,
            "form": form,
        }
        return render(request, "news/shotgun_edit.html", context)

    if request.method == "POST":
        form = AddShotgun(
            clubs,
            request.POST,
            request.FILES,
        )
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("news:shotguns"))


@login_required
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
        return HttpResponseRedirect(reverse("news:shotguns_admin"))


@login_required
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
                "edit": True,
            }
            return render(request, "news/shotgun_edit.html", context)

        if request.method == "POST":
            form = AddShotgun(
                [shotgun.club], request.POST, request.FILES, instance=shotgun
            )
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(
                    reverse("news:shotguns_admin_detail", args=(shotgun.id,))
                )
    else:
        raise PermissionDenied()


@login_required
def publish_shotgun_results(request, shotgun_id):
    student = get_object_or_404(Student, user__id=request.user.id)
    shotgun = get_object_or_404(Shotgun, pk=shotgun_id)
    if shotgun.club.is_admin(student.id):
        shotgun.motivations_review_finished = True
        shotgun.save()
        return HttpResponseRedirect(
            reverse("news:shotguns_admin_detail", args=(shotgun.id,))
        )
    else:
        raise PermissionDenied()


@login_required
def markdown(request):
    return render(request, "news/markdown.html")
