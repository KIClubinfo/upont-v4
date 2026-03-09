from django.contrib import admin

from .models import (
    Category,
    Channel,
    ChannelJoinRequest,
    ClubLoanItem,
    Club,
    ClubRequest,
    Membership,
    Message,
    Nationality,
    NotificationToken,
    Promotion,
    Role,
    Student,
)


class StudentAdmin(admin.ModelAdmin):
    list_display = ("user", "promo", "department")
    list_filter = ("promo", "department")


class ClubAdmin(admin.ModelAdmin):
    list_display = ("name",)


class MembershipsAdmin(admin.ModelAdmin):
    list_display = ("student", "club", "role")
    list_filter = ("club", "role")


class ClubRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "student")


class NotificationTokenAdmin(admin.ModelAdmin):
    list_display = ("student", "token")


class MessageAdmin(admin.ModelAdmin):
    list_display = ("channel", "club", "author", "date")
    ordering = ("date",)
    list_filter = ("channel",)


class ChannelAdmin(admin.ModelAdmin):
    list_display = ("name", "club", "creator", "date")
    ordering = ("name",)


class ChannelJoinRequestAdmin(admin.ModelAdmin):
    list_display = ("channel", "student", "status", "date")
    list_filter = ("status", "channel")
    ordering = ("-date",)


class ClubLoanItemAdmin(admin.ModelAdmin):
    list_display = ("club", "name", "borrower", "borrowed_on", "due_on")
    list_filter = ("club", "due_on")
    search_fields = ("name", "borrower__user__first_name", "borrower__user__last_name")
    ordering = ("due_on", "club", "name")


admin.site.register(Message, MessageAdmin)
admin.site.register(Channel, ChannelAdmin)
admin.site.register(ChannelJoinRequest, ChannelJoinRequestAdmin)
admin.site.register(ClubLoanItem, ClubLoanItemAdmin)
admin.site.register(Promotion)
admin.site.register(Student, StudentAdmin)
admin.site.register(Nationality)
admin.site.register(Role)
admin.site.register(Membership, MembershipsAdmin)
admin.site.register(Category)
admin.site.register(Club, ClubAdmin)
admin.site.register(ClubRequest, ClubRequestAdmin)
admin.site.register(NotificationToken, NotificationTokenAdmin)
