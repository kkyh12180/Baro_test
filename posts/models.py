from django.db import models
from accounts.models import User
from django.utils import timezone
from projects.models import Project

# Create your models here.
class Post(models.Model):
    post_id = models.CharField(primary_key=True, max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='post')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=False, related_name='post')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    post_time = models.DateTimeField(auto_now_add=True)
    like_number = models.IntegerField(default=0)

    class Meta:
        db_table = 'post'

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_like')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_like')
    post_like_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'post_like'