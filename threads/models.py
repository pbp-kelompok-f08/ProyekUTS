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

    liked_by = models.ManyToManyField(
        CustomUser,
        related_name='liked_threads',
        blank=True
    )

    def changeLike(self,user):
        if(user in self.liked_by.all()):
            self.likeCount -=1
            self.liked_by.remove(user)
            self.save()
            return False
        else:
            self.likeCount +=1
            self.liked_by.add(user)
            self.save()
            return True

    def changeShare(self,isInc):
        self.shareCount += 1 if isInc else -1
        self.save()

    def changeReply(self,isInc):
        self.replyCount += 1 if isInc else -1
        self.save()

class ReplyChild(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="replies")
    content = models.TextField()

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    likeCount = models.PositiveIntegerField(default=0)

    liked_by = models.ManyToManyField(
        CustomUser,
        related_name='liked_replies',
        blank=True
    )

    def changeLike(self,user):
        if(user in self.liked_by.all()):
            self.likeCount -=1
            self.liked_by.remove(user)
            self.save()
            return False
        else:
            self.likeCount +=1
            self.liked_by.add(user)
            self.save()
            return True


