from django.db import models
import uuid

# Create your models here.
class User(models.Model):
    pass

class Group(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(blank=False)
    users = models.ManyToManyField(to=User)

class Chat(models.Model):
    group_id = models.ForeignKey(to=Group, on_delete=models.CASCADE, related_name='chat')
    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='chat')
    message = models.TextField(blank=False)
    createdAt = models.DateTimeField(auto_now_add=True)