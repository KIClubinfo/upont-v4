from django.contrib import admin

from .models import Comment, Event, Participation, Post, Shotgun


class EventsAdmin(admin.ModelAdmin):
    list_display = ("name", "club", "date")
    list_filter = ("club",)
    ordering = ("date",)


class PostsAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "date")
    ordering = ("date", )


class ParticipationAdmin(admin.ModelAdmin):
    list_display = ("participant", "shotgun", "shotgun_date")
    ordering = ("shotgun_date",)


class ShotgunAdmin(admin.ModelAdmin):
    list_display = ("title", "club", "starting_date", "ending_date")
    list_filter = ("club",)
    ordering = ("starting_date",)


admin.site.register(Event, EventsAdmin)
admin.site.register(Post, PostsAdmin)
admin.site.register(Comment)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(Shotgun, ShotgunAdmin)
