from django.db import models
from account.models import User
from django.utils import timezone
from projects.models import Project

# Create your models here.
class Post(models.Model):
    # TODO post_id는 P로 시작해야함! 로직 수정 때 확인
    post_id = models.CharField(primary_key=True, max_length=10)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='post')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, related_name='post')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    post_time = models.DateTimeField(auto_now_add=True)
    like_number = models.IntegerField(blank=True, null=True)
    subscribe_only = models.BooleanField(default=False)

    class Meta:
        db_table = 'post'

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_like')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_like')
    post_like_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'post_like'