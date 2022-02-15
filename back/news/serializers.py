from django.urls import reverse
from rest_framework import serializers
from social.serializers import ClubSerializer, StudentSerializer

from .models import Comment, Post


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    author = StudentSerializer()
    club = ClubSerializer()

    class Meta:
        model = Comment
        fields = ["content", "author", "club", "date", "content"]


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
        return reverse("news:event_detail", args=(obj.pk,))

    total_likes = serializers.SerializerMethodField()

    def get_total_likes(self, obj):
        return obj.total_likes()

    total_comments = serializers.SerializerMethodField()

    def get_total_comments(self, obj):
        return obj.total_comments()

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
            "total_likes",
            "total_comments",
            "comments",
            "id",
        ]
