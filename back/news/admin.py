from django.contrib import admin

from .models import Comment, Event, Post, Shotgun

admin.site.register(Event)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Shotgun)
