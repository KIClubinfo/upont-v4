import json
import operator
import re
from datetime import datetime
from functools import reduce

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, Resource
from social.models import Club, Membership, Promotion, Student
from upont.regex import split_then_markdownify

from .forms import AddShotgun, CommentForm, EditEvent, EditPost  # , EditSondage
from .models import Participation  # , Sondage, OptionSondage
from .models import Comment, Event, Partnership, Post, Ressource, Shotgun
from .serializers import (
    EventSerializer,
    PartnershipSerializer,
    PostSerializer,
    ShotgunSerializer,
)

pattern = re.compile(
    r"^(http(s)?:\/\/)?((w){3}.)?youtu(be\.com\/watch\?v=|\.be\/)([A-Za-z0-9_\-]{11})$"
)

""" Utility function, same as in social -> views.py """


@login_required
def posts(request):
    try:
        student = Student.objects.get(user=request.user)
        if not student.is_validated:
            logout(request)
            messages.warning(
                request,
                "Votre compte étudiant n'est pas encore validé. Veuillez attendre la validation par un administrateur.",
            )
            return redirect(reverse_lazy("login"))
    except Student.DoesNotExist:
        user_to_delete = request.user
        user_to_delete.delete()
        logout(request)
        messages.warning(request, "Vous n'êtes pas autorisé à accéder à ce site.")
        return redirect(reverse_lazy("login"))
    if request.method == "GET":
        return render(request, "news/posts.html")


@login_required
def comment_post(request, post_id):
    if request.method == "POST":
        student = get_object_or_404(Student, user__id=request.user.id)
        data = json.loads(request.body.decode("utf-8"))
        commented_post = get_object_or_404(Post, id=post_id)
        filled_form = CommentForm(post_id, student.user.id, data=data)

        if filled_form.is_valid():
            new_comment = filled_form.save(commit=False)
            new_comment.post = commented_post
            new_comment.author = student
            new_comment.date = timezone.now()
            new_comment.save()
            return HttpResponse(status=201)
        return HttpResponse(status=500)
    else:
        return HttpResponse(status=400)


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows posts to be viewed.
    """

    serializer_class = PostSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        student = get_object_or_404(Student, user__id=self.request.user.id)
        promo = get_object_or_404(Promotion, pk=student.promo.pk)
        filter_date = datetime(promo.year + 2000 - 3, 8, 20, tzinfo=timezone.utc)
        queryset = Post.objects.filter(date__gt=filter_date)
        mode = self.request.GET.get("mode")
        bookmark = self.request.GET.get("bookmark")
        club = self.request.GET.get("club")
        if club is not None:
            club = get_object_or_404(Club, id=club)
            queryset = queryset.filter(club=club)
        if mode is None:
            queryset = queryset.order_by("-date", "title")
        elif mode == "social":
            queryset = queryset.filter(course__isnull=True).order_by("-date", "title")
            if bookmark:
                queryset = queryset.filter(bookmark=student)
        elif mode == "course":
            queryset = queryset.filter(course__isnull=False)

            course_id = self.request.GET.get("course_id")
            if course_id is not None:
                course = get_object_or_404(Course, id=course_id)
                queryset = queryset.filter(course=course)

            queryset = queryset.annotate(
                rank=Count("likes") - Count("dislikes")
            ).order_by("-rank", "-date")
        else:
            raise ValidationError(
                detail="mode argument must be eiter 'social' or 'course'"
            )

        return queryset


class BookmarkViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bookmarks to be viewed.
    """

    serializer_class = PostSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        student = get_object_or_404(Student, user__id=self.request.user.id)
        queryset = Post.objects.filter(bookmark=student).order_by("-date")
        return queryset


class ShotgunView(APIView):
    """
    API endpoint that returns avalaible shotguns for a logged student.
    """

    def get(self, request):
        # shotguns to which the user participated :
        student = get_object_or_404(Student, user__id=request.user.id)
        shotguns = Shotgun.objects.filter(ending_date__gte=timezone.now()).order_by(
            "starting_date"
        )
        serializer = ShotgunSerializer(
            shotguns, many=True, context={"student": student}
        )

        return Response({"shotguns": serializer.data})


class ShotgunParticipateView(APIView):
    """
    API endpoint to participate to a shotgun.
    """

    def post(self, request):
        shotgun = get_object_or_404(Shotgun, pk=request.data["shotgun"])
        student = Student.objects.get(user__id=request.user.id)
        if not shotgun.is_started():
            return Response({"status": "shotgun_not_started"})

        if shotgun.is_ended():
            return Response({"status": "shotgun_ended"})
        if shotgun.participated(student):
            return Response({"status": "already_participating"})
        if shotgun.requires_motivation:
            if "motivation" not in request.data:
                error_message = "Tu n'as pas fourni de motivation !"
                return Response({"status": "error", "message": error_message})

            participation = Participation(
                shotgun=shotgun,
                shotgun_date=timezone.now(),
                participant=student,
                motivation=request.data["motivation"],
            )
            participation.save()
        else:
            participation = Participation(
                shotgun=shotgun,
                shotgun_date=timezone.now(),
                participant=student,
            )
            participation.save()
            if shotgun.got_accepted(student):
                return Response({"status": "ok"})
            else:
                return Response({"status": "not_accepted"})
        return Response({"status": "ok"})


class PostReactionView(APIView):
    """
    API endpoint that allows users to react to posts.
    """

    def post(self, request):
        student = get_object_or_404(Student, user__id=request.user.id)
        post = get_object_or_404(Post, id=request.data["post"])
        if request.data["reaction"] == "like":
            post.likes.add(student)
            post.dislikes.remove(student)
        elif request.data["reaction"] == "unlike":
            post.likes.remove(student)
        elif request.data["reaction"] == "dislike":
            post.likes.remove(student)
            post.dislikes.add(student)
        elif request.data["reaction"] == "undislike":
            post.dislikes.remove(student)
        elif request.data["reaction"] == "bookmark":
            post.bookmark.add(student)
        elif request.data["reaction"] == "unbookmark":
            post.bookmark.remove(student)
        else:
            return Response({"status": "error", "message": "Invalid reaction"})
        post.save()
        return Response({"status": "ok"})


class PostCommentView(APIView):
    """
    API endpoint that allows students to comment posts
    """

    def post(self, request):
        student = get_object_or_404(Student, user__id=request.user.id)
        commented_post = get_object_or_404(Post, id=request.data["post"])
        comment = Comment(
            date=timezone.now(),
            author=student,
            post=commented_post,
            content=request.data["comment"],
        )
        comment.save()
        return Response({"status": "ok"})


class PostCreateView(APIView):
    def post(self, request):
        student = get_object_or_404(Student, user__id=request.user.id)
        post = Post(
            title=request.data["title"],
            author=student,
            date=timezone.now(),
            content=split_then_markdownify(request.data["content"]),
        )
        if request.data["title"] == "":
            return Response({"status": "error", "message": "empty_title"})
        elif request.data["content"] == "":
            return Response({"status": "error", "message": "empty_content"})

        post.save()
        return Response({"status": "ok"})


"""
class SondageCreateView(APIView):

    def post(self, request):
        if request.data["title"] == "":
            return Response({"status": "error", "message": "empty_title"})
        elif request.data["content"] == "":
            return Response({"status": "error", "message": "empty_content"})
        student = get_object_or_404(Student, user__id=request.user.id)

        if request.data["publish_as"] == "-1":
            sondage = Sondage(
                title=request.data["title"],
                author=student,
                date=timezone.now(),
                content=split_then_markdownify(request.data["content"]),
            )
        else:
            club = get_object_or_404(Club, id=request.data["publish_as"])
            if club.is_member(student.id):
                sondage = Sondage(
                    title=request.data["title"],
                    author=student,
                    club=club,
                    date=timezone.now(),
                    content=split_then_markdownify(request.data["content"]),
                )
            else:
                return Response({"status": "error", "message": "forbidden"})
            if request.data["options"] == []:
                return Response({"status": "error", "message": "empty_options"})
            else:
                i = 0
                for option in request.data["options"]:

                    if(option["text"] == ""):
                        return Response({"status": "error", "message": "empty_option_text"})
                    else:
                        option_sondage = OptionSondage(
                            sondage = sondage,
                            number = i,
                            text = option["text"],
                            )
                    option_sondage.save()
                    i+=1
        sondage.number_of_options = i
        sondage.save()
        return Response({"status": "ok"})
 """


class PostCreateViewV2(APIView):
    """
    API endpoint that allows students to create posts
    """

    def post(self, request):
        process_img = True
        if request.data["title"] == "":
            return Response({"status": "error", "message": "empty_title"})
        elif request.data["content"] == "":
            return Response({"status": "error", "message": "empty_content"})
        student = get_object_or_404(Student, user__id=request.user.id)
        if request.data["publish_as"] == "-1":
            post = Post(
                title=request.data["title"],
                author=student,
                date=timezone.now(),
                content=split_then_markdownify(request.data["content"]),
            )
            if "illustration" in request.data:
                post.illustration = request.data["illustration"]
            post.save()
        else:
            club = get_object_or_404(Club, id=request.data["publish_as"])
            if club.is_member(student.id):
                post = Post(
                    title=request.data["title"],
                    author=student,
                    club=club,
                    date=timezone.now(),
                    content=split_then_markdownify(request.data["content"]),
                )
                if "illustration" in request.data:
                    post.illustration = request.data["illustration"]
                post.save()
            else:
                process_img = False
                return Response({"status": "error", "message": "forbidden"})

        if (
            "resources_count" in request.data
            and int(request.data["resources_count"]) > 0
            and process_img
        ):
            resources = []
            for i in range(0, int(request.data["resources_count"])):
                resources.append(
                    {
                        "type": request.data["resources-" + str(i) + "-type"],
                        "data": request.data["resources-" + str(i) + "-data"],
                    }
                )
            for resource in resources:
                if resource["type"] == "video":
                    resource = Ressource(
                        title=request.data["title"],
                        post=post,
                        author=student,
                        video_url=resource["data"],
                    )
                elif resource["type"] == "image":
                    resource = Ressource(
                        title=request.data["title"],
                        post=post,
                        author=student,
                        image=resource["data"],
                    )
                resource.save()

        return Response({"status": "ok"})


class ShotgunCreateView(APIView):
    """
    API endpoint to create a shotgun (only for club admins).
    """

    def post(self, request):
        student = get_object_or_404(Student, user__id=request.user.id)

        # Vérifier les clubs où l'étudiant est admin
        admin_clubs_memberships = Membership.objects.filter(
            student__pk=student.id, is_admin=True
        )
        admin_clubs = [m.club for m in admin_clubs_memberships]

        if not admin_clubs:
            return Response(
                {"status": "error", "message": "not_admin"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Champs obligatoires (sécurisés)
        title = request.data.get("title", "").strip()
        content = request.data.get("content", "").strip()
        club_id = request.data.get("club")

        if not title:
            return Response({"status": "error", "message": "empty_title"}, status=400)
        if not content:
            return Response({"status": "error", "message": "empty_content"}, status=400)
        if not club_id:
            return Response({"status": "error", "message": "no_club"}, status=400)

        club = get_object_or_404(Club, id=club_id)

        # Vérifier que l’étudiant est admin du club choisi
        if club not in admin_clubs:
            return Response(
                {"status": "error", "message": "forbidden"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Dates
        starting_date = (
            parse_datetime(request.data.get("starting_date")) or timezone.now()
        )
        ending_date = parse_datetime(request.data.get("ending_date"))

        if not ending_date:
            return Response(
                {"status": "error", "message": "no_ending_date"},
                status=400,
            )

        # Bool (React Native -> string)
        requires_motivation = request.data.get("requires_motivation") in [
            True,
            "true",
            "True",
            "1",
            1,
        ]

        # Messages optionnels
        success_message = split_then_markdownify(
            request.data.get("success_message", "")
        )
        failure_message = split_then_markdownify(
            request.data.get("failure_message", "")
        )

        # Taille (si existante)
        size = request.data.get("size")
        size = int(size) if size else None

        # Création du shotgun
        shotgun = Shotgun(
            club=club,
            title=title,
            content=split_then_markdownify(content),
            starting_date=starting_date,
            ending_date=ending_date,
            requires_motivation=requires_motivation,
            success_message=success_message,
            failure_message=failure_message,
            size=size,
        )
        shotgun.save()

        return Response(
            {
                "status": "ok",
                "shotgun_id": shotgun.id,
                "message": "shotgun_created",
            },
            status=status.HTTP_201_CREATED,
        )


class PostEditView(APIView):
    """
    API endpoint that allows students to edit posts
    """

    def post(self, request):
        process_img = True
        if "title" not in request.data or request.data["title"] == "":
            return Response({"status": "error", "message": "empty_title"})
        elif "content" not in request.data or request.data["content"] == "":
            return Response({"status": "error", "message": "empty_content"})
        elif "post" not in request.data:
            return Response({"status": "error", "message": "no_post"})
        student = get_object_or_404(Student, user__id=request.user.id)
        post = get_object_or_404(Post, id=request.data["post"])
        if "publish_as" not in request.data:
            return Response({"status": "error", "message": "no_publish_as"})
        if request.data["publish_as"] == "-1":
            post.title = request.data["title"]
            post.content = split_then_markdownify(request.data["content"])
            post.club = None
            if "illustration" in request.data:
                post.illustration = request.data["illustration"]
            else:
                post.illustration = None
            post.save()
        else:
            club = get_object_or_404(Club, id=request.data["publish_as"])
            if club.is_member(student.id):
                post.title = request.data["title"]
                post.content = split_then_markdownify(request.data["content"])
                post.club = club
                if "illustration" in request.data:
                    post.illustration = request.data["illustration"]
                else:
                    post.illustration = None
                post.save()
            else:
                process_img = False
                return Response({"status": "error", "message": "forbidden"})

        if (
            "resources_count" in request.data
            and int(request.data["resources_count"]) > 0
            and process_img
        ):
            Ressource.objects.filter(post=post).delete()
            resources = []
            for i in range(0, int(request.data["resources_count"])):
                resources.append(
                    {
                        "type": request.data["resources-" + str(i) + "-type"],
                        "data": request.data["resources-" + str(i) + "-data"],
                    }
                )
            for resource in resources:
                if resource["type"] == "video":
                    resource = Ressource(
                        title=request.data["title"],
                        post=post,
                        author=student,
                        video_url=resource["data"],
                    )
                elif resource["type"] == "image":
                    resource = Ressource(
                        title=request.data["title"],
                        post=post,
                        author=student,
                        image=resource["data"],
                    )
                resource.save()
        if "kept_resources" in request.data and process_img:
            current_resources = Ressource.objects.all().filter(post=post)
            for resource in current_resources:
                if resource.id not in request.data["kept_resources"]:
                    resource.delete()
        return Response({"status": "ok"})


class PostDeleteView(APIView):
    """
    API endpoint that allows students or moderators to delete posts
    """

    def post(self, request):
        student = get_object_or_404(Student, user__id=request.user.id)
        post = get_object_or_404(Post, id=request.data["post"])
        if (
            post.author == student
            or (post.club is not None and post.club.is_admin(student.id))
            or student.is_moderator
        ):
            post.delete()
            return Response({"status": "ok"})
        else:
            return Response({"status": "error", "message": "not_allowed"})


class DeleteCommentView(APIView):
    """
    API endpoint that allows students or moderators to delete comments
    """

    def post(self, request):
        student = get_object_or_404(Student, user__id=request.user.id)
        comment = get_object_or_404(Comment, id=request.data["comment"])
        if (
            comment.author == student
            or (comment.club is not None and comment.club.is_admin(student.id))
            or student.is_moderator
        ):
            comment.delete()
            return Response({"status": "ok"})
        else:
            return Response({"status": "error", "message": "not_allowed"})


class PartnershipViewSet(viewsets.ModelViewSet):
    serializer_class = PartnershipSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = Partnership.objects.all()
        club = self.request.GET.get("club")
        if club is not None:
            club = get_object_or_404(Club, id=club)
            queryset = queryset.filter(club=club)
        return queryset


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
    """

    serializer_class = EventSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = Event.objects.all()

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

        return queryset.order_by("date", "name").filter(end__gte=timezone.now())


class SearchPost(APIView):
    """
    API endpoint that returns the posts whose content or title contains the query.
    """

    def get(self, request):
        student = get_object_or_404(Student, user__id=request.user.id)
        promo = get_object_or_404(Promotion, pk=student.promo.pk)
        filter_date = datetime(promo.year + 2000 - 3, 8, 20, tzinfo=timezone.utc)
        if "post" in request.GET and request.GET["post"].strip():
            found_posts, searched_expression = search_post(request)
            result = [post for post in found_posts if post.date > filter_date][:15]
        else:
            result = Post.objects.filter(date__gt=filter_date).order_by("-date")[:15]
        serializer = PostSerializer(result, many=True, context={"request": request})
        return Response({"posts": serializer.data})


def search_post(request):
    searched_expression = request.GET.get("post", None)
    key_words_list = [word.strip() for word in searched_expression.split()]

    if not key_words_list:
        return Post.objects.none(), searched_expression

    # Créer des conditions pour chaque mot-clé
    content_conditions = [Q(content__icontains=word) for word in key_words_list]
    title_conditions = [Q(title__icontains=word) for word in key_words_list]

    # Combiner les conditions avec OR pour chaque champ
    content_query = reduce(operator.or_, content_conditions)
    title_query = reduce(operator.or_, title_conditions)

    # Combiner les requêtes de contenu et de titre avec OR
    combined_query = content_query | title_query

    # Effectuer la recherche
    found_items = Post.objects.filter(combined_query).distinct()
    found_items = found_items.order_by("-date")

    return found_items, searched_expression


@login_required
def events(request):
    student = get_object_or_404(Student, user__id=request.user.id)
    all_events_list = Event.objects.filter(end__gte=timezone.now()).order_by("date")
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
def post_edit(request, post_id, course_id=None):
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
                videos = Ressource.objects.filter(post=post, video_url__isnull=False)
                if request.POST["video"] == "" and len(videos) >= 1:
                    videos.first().delete()
                elif request.POST["video"] != "":
                    resources = Ressource.objects.filter(
                        post=post, video_url__isnull=False
                    )
                    if len(resources) >= 1 and pattern.match(request.POST["video"]):
                        resource = resources.first()
                        resource.video_url = request.POST["video"]
                        resource.save()
                    else:
                        if pattern.match(request.POST["video"]):
                            resource = Ressource(
                                title=request.POST["title"],
                                post=post,
                                author=student,
                                video_url=request.POST["video"],
                            )
                            resource.save()
                resources = Ressource.objects.filter(post=post)
                if "illustration" in request.FILES:
                    images = Ressource.objects.filter(post=post, image__isnull=False)
                    if len(images) >= 1:
                        image = images.first()
                        image.image = request.FILES["illustration"]
                        image.save()
                    else:
                        resource = Ressource(
                            title=post.title,
                            post=post,
                            author=student,
                            image=request.FILES["illustration"],
                        )
                        resource.save()
                if course_id is not None and form.cleaned_data["resource_file"]:
                    post.resource.all().delete()
                    resource = Resource(
                        name=form.cleaned_data["resource_file"].name,
                        author=post.author,
                        date=post.date,
                        file=form.cleaned_data["resource_file"],
                        post=post,
                    )
                    resource.save()
                form.save()
                return redirect("news:posts")

    else:
        form = EditPost(request.user.id, instance=post)
        resources = Ressource.objects.filter(post=post)
        if len(resources) >= 1:
            form.fields["video"].initial = resources.first().video_url
    context["EditPost"] = form
    context["post"] = post
    context["Edit"] = True
    context["course_id"] = course_id
    request.session["origin"] = request.META.get("HTTP_REFERER", reverse("news:posts"))
    return render(request, "news/post_edit.html", context)


@login_required
def post_create(request, event_id=None, course_id=None):
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
                student = Student.objects.get(user__id=request.user.id)
                post.author = student
                post.date = timezone.now()
                post.content = split_then_markdownify(post.content)
                post.save()
                if "illustration" in request.FILES:
                    resource = Ressource(
                        title=request.POST["title"],
                        post=post,
                        author=student,
                        image=request.FILES["illustration"],
                    )
                    resource.save()

                elif request.POST["video"] != "":
                    if pattern.match(request.POST["video"]):
                        resource = Ressource(
                            title=post.title,
                            post=post,
                            author=student,
                            video_url=request.POST["video"],
                        )
                        resource.save()
                if course_id is not None:
                    course = get_object_or_404(Course, pk=course_id)
                    course.posts.add(post)
                if course_id is not None and form.cleaned_data["resource_file"]:
                    resource = Resource(
                        name=form.cleaned_data["resource_file"].name,
                        author=post.author,
                        date=post.date,
                        file=form.cleaned_data["resource_file"],
                        post=post,
                    )
                    resource.save()
                return HttpResponseRedirect(request.session["origin"])
    else:
        form = EditPost(request.user.id)
        if event_id is not None:
            form.fields["event"].initial = get_object_or_404(Event, id=event_id)
    request.session["origin"] = request.META.get("HTTP_REFERER", reverse("news:posts"))
    context["EditPost"] = form
    context["Edit"] = False
    context["course_id"] = course_id
    return render(request, "news/post_edit.html", context)


""" @login_required
def sondage_create(request):
    context = {}
    if request.method == "POST":
        if "Valider" in request.POST:
            form = EditSondage(
                request.user.id,
                request.POST,
                request.FILES,
            )
            if form.is_valid():
                post = form.save(commit=False)
                student = Student.objects.get(user__id=request.user.id)
                post.author = student
                post.date = timezone.now()
                post.content = split_then_markdownify(post.content)
                post.save()
                return HttpResponseRedirect(request.session["origin"])
    else:
        form = EditSondage(request.user.id)
    request.session["origin"] = request.META.get("HTTP_REFERER", reverse("news:sondages"))
    context["EditSondage"] = form
    context["Edit"] = False
    return render(request, "news/sondage_edit.html", context) """


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
    elif action == "Bookmark":
        post.bookmark.add(student)
    elif action == "Unbookmark":
        post.bookmark.remove(student)
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
            shotgun = form.save()
            shotgun.content = split_then_markdownify(shotgun.content)
            shotgun.success_message = split_then_markdownify(shotgun.success_message)
            shotgun.failure_message = split_then_markdownify(shotgun.failure_message)
            shotgun.save()
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
            form.fields["success_message"].initial = shotgun.success_message
            form.fields["failure_message"].initial = shotgun.failure_message
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
                shotgun = form.save()
                shotgun.content = split_then_markdownify(shotgun.content)
                shotgun.success_message = split_then_markdownify(
                    shotgun.success_message
                )
                shotgun.failure_message = split_then_markdownify(
                    shotgun.failure_message
                )
                shotgun.save()
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


@login_required
def bookmarks(request):
    return render(request, "news/bookmarks.html")
