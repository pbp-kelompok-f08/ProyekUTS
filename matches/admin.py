from django.contrib import admin

from .models import Match, Participation, SportCategory


@admin.register(SportCategory)
class SportCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "event_date", "max_members")
    list_filter = ("category", "event_date")
    search_fields = ("title", "location", "description")


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ("match", "created_at")
    search_fields = ("match__title",)
    list_filter = ("match",)
