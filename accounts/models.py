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
