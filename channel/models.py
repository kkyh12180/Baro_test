from django.db import models
from account.models import User
from django.utils import timezone

# Create your models here.
class ChannelPost(models.Model):
    channel_post_id = models.CharField(primary_key=True, max_length=10)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='channel_post')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    post_time = models.DateTimeField(auto_now_add=True)
    like_number = models.IntegerField(default=0)
    subscribe_only = models.BooleanField(default=False)

    class Meta:
        db_table = 'channel_post'

class ChannelPostLike(models.Model):
    post = models.ForeignKey(ChannelPost, on_delete=models.CASCADE, related_name='channel_post_like')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='channel_post_like')
    post_like_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'channel_post_like'