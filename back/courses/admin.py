from django.contrib import admin

from .models import Course, CourseUpdate, Enrolment, Group, Teacher, Resources


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

class RessourcesAdmin(admin.ModelAdmin):
    list_display=(
        "name",
        "author",
        "date",
        "file"
    )
    list_filter = ("course",)




admin.site.register(Course, CourseAdmin)
admin.site.register(CourseUpdate, CourseUpdateAdmin)
admin.site.register(Teacher)
admin.site.register(Group, GroupAdmin)
admin.site.register(Enrolment, EnrolmentAdmin)

