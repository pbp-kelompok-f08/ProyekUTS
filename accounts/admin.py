from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "role", "is_staff", "last_activity")
    list_filter = ("role", "is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "email", "bio", "profile_picture", "favorite_sport", "skill_level")}),
        ("Permissions", {"fields": ("role", "is_staff", "is_active", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "last_activity", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "role", "is_staff", "is_active"),
        }),
    )
    search_fields = ("username", "email")
    ordering = ("username",)
