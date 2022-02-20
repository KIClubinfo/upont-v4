from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import serializers
from social.models import Student
from social.serializers import ClubSerializer, StudentSerializer

from .models import Comment, Post


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    author = StudentSerializer()
    club = ClubSerializer()
    comment_delete_url = serializers.SerializerMethodField()

    def get_comment_delete_url(self, obj):
        return reverse("news:comment_delete", args=(obj.id,))

    is_my_comment = serializers.SerializerMethodField()

    def get_is_my_comment(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        if obj.author and obj.author.user.id == user.id:
            return True
        if obj.club and obj.club.is_member(obj.author.id):
            return True
        return False

    class Meta:
        model = Comment
        fields = [
            "content",
            "author",
            "club",
            "date",
            "content",
            "comment_delete_url",
            "is_my_comment",
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
            return reverse("news:event_detail", args=(obj.pk,))
        else:
            return False

    edit_url = serializers.SerializerMethodField()

    def get_edit_url(self, obj):
        return reverse("news:post_edit", args=(obj.pk,))

    like_url = serializers.SerializerMethodField()

    def get_like_url(self, obj):
        return reverse("news:post_like", args=(obj.pk, "Like"))

    dislike_url = serializers.SerializerMethodField()

    def get_dislike_url(self, obj):
        return reverse("news:post_like", args=(obj.pk, "Dislike"))

    total_likes = serializers.SerializerMethodField()

    def get_total_likes(self, obj):
        return obj.total_likes()

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

    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "title",
            "author",
            "club",
            "date",
            "illustration_url",
            "content",
            "event_url",
            "edit_url",
            "like_url",
            "dislike_url",
            "total_likes",
            "total_comments",
            "user_liked",
            "comments",
            "id",
        ]
