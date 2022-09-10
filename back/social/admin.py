from django.contrib import admin

from .models import (
    Category,
    Club,
    ClubRequest,
    Membership,
    Nationality,
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


admin.site.register(Promotion)
admin.site.register(Student, StudentAdmin)
admin.site.register(Nationality)
admin.site.register(Role)
admin.site.register(Membership, MembershipsAdmin)
admin.site.register(Category)
admin.site.register(Club, ClubAdmin)
admin.site.register(ClubRequest, ClubRequestAdmin)
