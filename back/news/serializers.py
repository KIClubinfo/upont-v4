from courses.serializers import ResourceSerializer
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import serializers
from social.models import Student
from social.serializers import ClubSerializer, StudentSerializer

from .models import Comment, Event, Post, Shotgun


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    author = StudentSerializer()
    club = ClubSerializer()

    is_my_comment = serializers.SerializerMethodField()

    def get_is_my_comment(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        student = get_object_or_404(Student, user__id=user.id)
        if (obj.club and obj.club.is_member(student.id)) or (
            not obj.club and obj.author.user.id == user.id
        ):
            return True
        return False

    author_url = serializers.SerializerMethodField()

    def get_author_url(self, obj):
        if obj.club:
            return reverse("social:club_detail", args=(obj.club.pk,))
        else:
            return reverse("social:profile_viewed", args=(obj.author.user.pk,))

    user_author_url = serializers.SerializerMethodField()

    def get_user_author_url(self, obj):
        return reverse("social:profile_viewed", args=(obj.author.user.pk,))

    class Meta:
        model = Comment
        fields = [
            "content",
            "author",
            "club",
            "date",
            "content",
            "is_my_comment",
            "author_url",
            "user_author_url",
            "id",
        ]


class PostSerializer(serializers.HyperlinkedModelSerializer):
    author = StudentSerializer()
    club = ClubSerializer()
    illustration_url = serializers.SerializerMethodField()

    def get_illustration_url(self, obj):
        if obj.illustration:
            return obj.illustration.url
        else:
            return False

    event_url = serializers.SerializerMethodField()

    def get_event_url(self, obj):
        if obj.event:
            return reverse("news:event_detail", args=(obj.event.pk,))
        else:
            return False

    event_name = serializers.SerializerMethodField()

    def get_event_name(self, obj):
        if obj.event:
            return obj.event.name
        else:
            return False

    edit_url = serializers.SerializerMethodField()

    def get_edit_url(self, obj):
        if not obj.course.all():
            return reverse("news:post_edit", args=(obj.pk,))
        else:
            course_id = obj.course.all()[0].id
            return reverse("courses:course_post_edit", args=(course_id, obj.pk))

    author_url = serializers.SerializerMethodField()

    def get_author_url(self, obj):
        if obj.club:
            return reverse("social:club_detail", args=(obj.club.pk,))
        else:
            return reverse("social:profile_viewed", args=(obj.author.user.pk,))

    like_url = serializers.SerializerMethodField()

    def get_like_url(self, obj):
        return reverse("news:post_like", args=(obj.pk, "Like"))

    unlike_url = serializers.SerializerMethodField()

    def get_unlike_url(self, obj):
        return reverse("news:post_like", args=(obj.pk, "Unlike"))

    undislike_url = serializers.SerializerMethodField()

    def get_total_likes(self, obj):
        return obj.total_likes()

    dislike_url = serializers.SerializerMethodField()

    def get_dislike_url(self, obj):
        return reverse("news:post_like", args=(obj.pk, "Dislike"))

    undislike_url = serializers.SerializerMethodField()

    def get_undislike_url(self, obj):
        return reverse("news:post_like", args=(obj.pk, "Undislike"))

    total_dislikes = serializers.SerializerMethodField()

    def get_total_dislikes(self, obj):
        return obj.total_dislikes()

    total_comments = serializers.SerializerMethodField()

    def get_total_comments(self, obj):
        return obj.total_comments()

    user_liked = serializers.SerializerMethodField()

    def get_user_liked(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        student = get_object_or_404(Student, user__id=user.id)
        if student and student in obj.likes.all():
            return True
        return False

    user_disliked = serializers.SerializerMethodField()

    def get_user_disliked(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        student = get_object_or_404(Student, user__id=user.id)
        if student and student in obj.dislikes.all():
            return True
        return False

    comments = CommentSerializer(many=True, read_only=True)

    can_edit = serializers.SerializerMethodField()

    def get_can_edit(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        student = get_object_or_404(Student, user__id=user.id)
        if (
            obj.club and obj.club.is_member(student.id)
        ) or obj.author.user.id == user.id:
            return True
        return False

    user_author_url = serializers.SerializerMethodField()

    def get_user_author_url(self, obj):
        return reverse("social:profile_viewed", args=(obj.author.user.pk,))

    resource = ResourceSerializer(many=True, read_only=True)

    user_bookmarked = serializers.SerializerMethodField()

    def get_user_bookmarked(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        student = get_object_or_404(Student, user__id=user.id)
        if student and student in obj.bookmark.all():
            return True
        return False

    bookmark_url = serializers.SerializerMethodField()

    def get_bookmark_url(self, obj):
        return reverse("news:post_like", args=(obj.pk, "Bookmark"))

    unbookmark_url = serializers.SerializerMethodField()

    def get_unbookmark_url(self, obj):
        return reverse("news:post_like", args=(obj.pk, "Unbookmark"))

    class Meta:
        model = Post
        fields = [
            "title",
            "author",
            "club",
            "date",
            "illustration_url",
            "content",
            "event_name",
            "event_url",
            "edit_url",
            "author_url",
            "like_url",
            "unlike_url",
            "total_likes",
            "dislike_url",
            "undislike_url",
            "total_dislikes",
            "total_comments",
            "user_liked",
            "user_disliked",
            "comments",
            "id",
            "can_edit",
            "user_author_url",
            "resource",
            "bookmark_url",
            "unbookmark_url",
            "user_bookmarked",
        ]


class ShotgunSerializer(serializers.HyperlinkedModelSerializer):
    club = ClubSerializer()

    user_state = serializers.SerializerMethodField()

    def get_user_state(self, obj):
        if obj.participated(self.context.get("student")):
            if not obj.requires_motivation:
                if obj.got_accepted(self.context.get("student")):
                    return "accepted"
                else:
                    return "failed"
            else:
                if obj.motivations_review_finished:
                    if obj.got_accepted(self.context.get("student")):
                        return "accepted"
                    else:
                        return "failed"
                else:
                    return "waiting"
        else:
            return "not_participated"

    id = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.pk

    class Meta:
        model = Shotgun
        fields = [
            "id",
            "title",
            "club",
            "content",
            "starting_date",
            "ending_date",
            "size",
            "requires_motivation",
            "motivations_review_finished",
            "user_state",
        ]


class EventSerializer(serializers.HyperlinkedModelSerializer):
    club = ClubSerializer()
    shotgun = ShotgunSerializer()

    class Meta:
        model = Event
        fields = [
            "name",
            "description",
            "club",
            "date",
            "end",
            "location",
            "participants",
            "poster",
            "shotgun",
            "id",
        ]
