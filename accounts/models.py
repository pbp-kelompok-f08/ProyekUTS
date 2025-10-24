from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    username = models.CharField(max_length=255, primary_key=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', blank=True)

    # Profile Info
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    favorite_sport = models.CharField(max_length=50, blank=True, null=True)
    skill_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ], blank=True, null=True)

    @property
    def participation(self):
        participations = self.participations.all()
        data = []
        for participation in participations:
            data.append({
                "match": participation.match.id,
                "group": participation.match.group.id,
                "created_at":participation.created_at
            })
        return data

    def __str__(self):
        return f"{self.username} ({self.role})"
