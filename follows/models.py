from django.db import models
from accounts.models import User
from images.models import ImagePost
from django.utils import timezone
from search.models import Prompt

# Create your models here.
class BookmarkImagePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_post = models.ForeignKey(ImagePost, on_delete=models.CASCADE)
    bookmark_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'bookmark_image_post'

class LikeImagePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_post = models.ForeignKey(ImagePost, on_delete=models.CASCADE)
    like_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'like_image_post'

class FollowUploader(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_uploader')
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    follow_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'follow_uploader'

class SubscribeUploader(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribed_uploader')
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriber')
    subscribe_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'subscribe_uploader'

class BookmarkPrompt(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='bookmark_prompt')
    prompt = models.ForeignKey(Prompt, models.CASCADE, related_name='bookmark_prompt')
    is_positive = models.IntegerField()
    bookmark_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'bookmark_prompt'

class PromptRecommend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='prompt_recommend')
    similar_prompt = models.TextField(blank=True, null=True)
    conflict_prompt = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'prompt_recommend'