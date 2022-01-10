from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from social.models import Membership, Student

from .forms import EditEvent, EditPost
from .models import Event, Post


def posts(request):
    all_posts_list = Post.objects.order_by("-date")
    context = {"all_posts_list": all_posts_list}
    return render(request, "news/posts.html", context)


def events(request):
    all_events_list = Event.objects.order_by("-date")
    context = {"all_events_list": all_events_list}
    return render(request, "news/events.html", context)


def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    event_posts = Post.objects.filter(event__pk=event_id).order_by("-date")
    context = {"event": event, "event_posts": event_posts}
    return render(request, "news/event_detail.html", context)


@login_required(login_url="/login/")
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
        if "Annuler" in request.POST:
            return redirect("news:event_detail", event_id=event.id)
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
    return render(request, "news/event_edit.html", context)


@login_required(login_url="/login/")
def event_create(request):
    context = {}
    if request.method == "POST":
        if "Annuler" in request.POST:
            return redirect("news:events")
        elif "Valider" in request.POST:
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


@login_required(login_url="/login/")
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {}
    if request.method == "POST":
        if "Annuler" in request.POST:
            return redirect("news:post_detail", post_id=post.id)
        elif "Valider" in request.POST:
            form = EditPost(
                request.user.id,
                request.POST,
                request.FILES,
                instance=Post.objects.get(id=post_id),
            )
            if form.is_valid():
                if "illustration" in request.FILES:
                    post.poster.delete()
                form.save()
                return redirect("news:posts")

    else:
        form = EditPost(request.user.id, instance=post)
    context["EditPost"] = form
    return render(request, "news/post_edit.html", context)


@login_required(login_url="/login/")
def post_create(request):
    context = {}
    if request.method == "POST":
        if "Annuler" in request.POST:
            return redirect("news:posts")
        elif "Valider" in request.POST:
            form = EditPost(
                request.user.id,
                request.POST,
                request.FILES,
            )
            if form.is_valid():
                post = form.save(commit=False)
                post.published_as_student = False
                post.date = datetime.now()
                post.save()
                return redirect("news:posts")
    else:
        form = EditPost(request.user.id)
    context["EditPost"] = form
    return render(request, "news/post_edit.html", context)
