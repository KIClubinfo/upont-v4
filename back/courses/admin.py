from django.contrib import admin

from .models import Course, CourseUpdate, Enrolment, Group, Resource, Teacher, Timeslot


class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "acronym", "department")
    list_filter = ("department",)


class CourseUpdateAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "old_course",
        "new_course",
    )


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        "course",
        "teacher",
    )
    list_filter = ("course",)


class EnrolmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "group",
    )


class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "date",
        "post",
    )


class TimeslotAdmin(admin.ModelAdmin):
    list_display = (
        "start",
        "end",
        "place",
    )
    list_filter = ("course_groups",)


admin.site.register(Course, CourseAdmin)
admin.site.register(CourseUpdate, CourseUpdateAdmin)
admin.site.register(Teacher)
admin.site.register(Group, GroupAdmin)
admin.site.register(Enrolment, EnrolmentAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(Timeslot, TimeslotAdmin)
