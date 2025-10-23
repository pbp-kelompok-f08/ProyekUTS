from django.db import models
from django.utils.text import slugify
from accounts.models import CustomUser
import uuid

class SportCategory(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Match(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=120)
    category = models.ForeignKey(
        to=SportCategory, on_delete=models.CASCADE, related_name="matches"
    )
    location = models.CharField(max_length=150)
    event_date = models.DateTimeField()
    description = models.TextField(blank=True)
    max_members = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["event_date"]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.title

    @property
    def current_members(self) -> int:
        return self.participations.count()

    @property
    def available_slots(self) -> int:
        return max(self.max_members - self.current_members, 0)

class Participation(models.Model):
    match = models.ForeignKey(
        Match, on_delete=models.CASCADE, related_name="participations"
    )
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name="participations")
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.user.username} - {self.match.id}"