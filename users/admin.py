from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department, Profile

# Extend UserAdmin to show the Department field in the admin panel
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_teacher', 'department')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_teacher', 'department')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Department)
admin.site.register(Profile)