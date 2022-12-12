from django.contrib import admin

from .models import Course, Enrolment, Group, Teacher, Update


class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "acronym", "department")
    list_filter = ("department",)


class UpdateAdmin(admin.ModelAdmin):
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
        "course",
    )


admin.site.register(Course, CourseAdmin)
admin.site.register(Update, UpdateAdmin)
admin.site.register(Teacher)
admin.site.register(Group, GroupAdmin)
admin.site.register(Enrolment, EnrolmentAdmin)
