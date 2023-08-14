from django.db import models
from account.models import User
from django.utils import timezone

# Create your models here.

class ImagePost(models.Model):
    image_post_id = models.CharField(primary_key=True, max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_post')
    thumbnail_image = models.CharField(max_length=512)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    post_time = models.DateTimeField(auto_now_add=True)
    like_number = models.IntegerField(default=0)
    adult = models.BooleanField(default=False)
    subscribe_only = models.BooleanField(default=False)

    class Meta:
        db_table = 'image_post'

class ImageTable(models.Model):
    image_id = models.CharField(unique=True, max_length=10)
    image_post_id = models.ForeignKey(ImagePost, on_delete=models.CASCADE, related_name='image')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image')
    image_file = models.CharField(max_length=512)
    seed = models.CharField(default=None, max_length=30, blank=True, null=True)
    steps = models.IntegerField(default=None, blank=True, null=True)
    sampler = models.CharField(default=None, max_length=30, blank=True, null=True)
    cfg_scale = models.FloatField(default=None, blank=True, null=True)
    model_hash = models.CharField(default=None, max_length=30, blank=True, null=True)
    clip_skip = models.IntegerField(default=None, blank=True, null=True)
    denoising_strength = models.FloatField(default=None, blank=True, null=True)
    image_time = models.DateTimeField(auto_now_add=True)
    adult = models.BooleanField(default=False)

    class Meta:
        db_table = 'image_table'
        unique_together = ('image_id', 'image_post_id')

class ImagePrompt(models.Model):
    image = models.ForeignKey(ImageTable, default=None, on_delete=models.CASCADE, related_name='prompt', null=True)
    prompt = models.TextField()
    is_positive = models.BooleanField(null=True)
    prompt_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'image_prompt'