from django.contrib import admin
from .models import Group, Chat

# Register your models here.
# @admin.register(Group)
# class GroupAdmin(admin.ModelAdmin):
#     list_display = ("title", "category", "event_date", "max_members")
#     list_filter = ("category", "event_date")
#     search_fields = ("title", "location", "description")


# @admin.register(Chat)
# class ChatAdmin(admin.ModelAdmin):
#     list_display = ("match", "created_at")
#     search_fields = ("match__title",)
#     list_filter = ("match",)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("match", "name")
    list_filter = ("match", "name")
    search_fields = ("name",)


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("username", "group_id", "message", "createdAt")
    search_fields = ("uername", "group_id", "createdAt")
    list_filter = ("createdAt",)