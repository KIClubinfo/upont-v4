from django.contrib import admin

from .models import Comment, Event, Participation, Post, Shotgun

admin.site.register(Event)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Participation)
admin.site.register(Shotgun)
