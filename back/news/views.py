from datetime import datetime

# from django.utils import timezone
# from django.urls import reverse
# from django.views import View
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from social.models import Membership, Student

from .forms import EditEvent, EditPost, CommentForm
from .models import Event, Post, Comment


def posts(request):
    student = get_object_or_404(Student, user__id=request.user.id)
    all_posts_list = Post.objects.order_by("-date")
    membership_club_list = Membership.objects.filter(student__pk=student.id)

    my_posts = Post.objects.filter(author__pk=student.id, club=None)

    for membership in membership_club_list:
        my_posts |= Post.objects.filter(club=membership.club)

    context = {
        "all_posts_list": all_posts_list,
        "my_posts": my_posts
    }
    return render(request, "news/posts.html", context)

# class Posts(View):
#     def get(self, request):
#         all_posts_list = Post.objects.order_by("-date")
#         all_posts_and_forms = [(post, CommentForm()) for post in all_posts_list]
#         context = {"all_posts_and_forms": all_posts_and_forms}
#         return render(request, "news/posts.html", context)
#
#     def post(self, request):
#         comment_form = CommentForm(data=request.POST)
#         if comment_form.is_valid():
#             new_comment = comment_form.save(commit=False)
#             new_comment.date = timezone.now()
#             new_comment.save()
#             return redirect(reverse("news:posts"))
#         else:
#             all_posts_list = Post.objects.order_by("-date")
#             all_posts_and_forms = [(post, CommentForm()) for post in all_posts_list]
#             commented_post = request.POST.get("post")
#             print(type(commented_post))
#             print(commented_post)
#             commented_post_index = 0
#             for index, post in enumerate(all_posts_list):
#                 if post == commented_post:
#                     commented_post_index = index
#             all_posts_and_forms[commented_post_index] = (commented_post, comment_form)
#             context = {"all_posts_and_forms": all_posts_and_forms}
#             return render(request, "news/posts.html", context)


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
        elif "Supprimer" in request.POST:
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
    student = get_object_or_404(Student, user__id=request.user.id)
    post = get_object_or_404(Post, pk=post_id)

    if post.club:
        membership_club_list = Membership.objects.filter(
            student__pk=student.id, club__pk=post.club.id
        )
        if not membership_club_list:  # If no match is found
            raise PermissionDenied
    else:
        if post.author.user.id != request.user.id:
            raise PermissionDenied

    post = get_object_or_404(Post, id=post_id)
    context = {}
    if request.method == "POST":
        if "Annuler" in request.POST:
            return redirect("news:posts")
        elif "Supprimer" in request.POST:
            post.delete()
            return redirect("news:posts")
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
    context["Edit"] = True
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
                post.author = Student.objects.get(user__id=request.user.id)
                post.date = datetime.now()
                post.save()
                return redirect("news:posts")
    else:
        form = EditPost(request.user.id)
    context["EditPost"] = form
    context["Edit"] = False
    return render(request, "news/post_edit.html", context)


@login_required(login_url="/login/")
def post_like(request, post_id, action):
    post = get_object_or_404(Post, id=post_id)
    student = get_object_or_404(Student, user__id=request.user.id)
    if action == "Dislike":
        post.likes.remove(student)
    elif action == "Like":
        post.likes.add(student)
    return redirect("news:posts")
