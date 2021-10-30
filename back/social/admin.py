from django.contrib import admin

from .models import Promotion, Student, Nationality, Role, Membership, Category, Club


class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'promo',
        'clubs',
        'department'
    )


class ClubAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'membres'
    )


admin.site.register(Promotion)
admin.site.register(Student, StudentAdmin)
admin.site.register(Nationality)
admin.site.register(Role)
admin.site.register(Membership)
admin.site.register(Category)
admin.site.register(Club, ClubAdmin)