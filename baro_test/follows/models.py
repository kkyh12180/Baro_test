from django.db import models
from account.models import User
from images.models import ImagePost
from django.utils import timezone

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

'''
class BookmarkPrompt(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING)
    prompt = models.ForeignKey('Prompt', models.DO_NOTHING, db_column='prompt')
    is_positive = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'bookmark_prompt'
'''