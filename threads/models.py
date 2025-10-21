import uuid
from django.db import models
from django.conf import settings
from accounts.models import CustomUser

class Thread(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField()
    tags = models.TextField()
    image = models.URLField(blank=True, null=True)
    likeCount = models.PositiveIntegerField(default=0)
    shareCount = models.PositiveIntegerField(default=0)
    replyCount = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def changeLike(self,isInc):
        self.likeCount += 1 if isInc else -1
        self.save()

    def changeShare(self,isInc):
        self.shareCount += 1 if isInc else -1
        self.save()
    def changeReply(self,isInc):
        self.replyCount += 1 if isInc else -1
        self.save()

class Reply(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="replies")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField()
    image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likeCount = models.PositiveIntegerField(default=0)

    def changeLike(self,isInc):
        self.likeCount += 1 if isInc else -1
        self.save()

class ReplyChild(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)

    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, related_name="child_replies")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likeCount = models.PositiveIntegerField(default=0)

    def changeLike(self,isInc):
        self.likeCount += 1 if isInc else -1
        self.save()


