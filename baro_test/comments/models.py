from django.db import models
from account.models import User
from images.models import ImagePost

# Create your models here.

# TODO Comment PK 작성 로직 필요 (views.py에서 진행)
class Comment(models.Model):
    comment_id = models.CharField(primary_key=True, max_length=15)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='comment')
    content = models.TextField(blank=True, null=False)
    comment_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comment'

class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_like')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_like')
    comment_like_time = models.DateTimeField(auto_now_add=True)
    is_good = models.BooleanField(default=True)

    class Meta:
        db_table = 'comment_like'

class ImageComment(models.Model):
    image_post = models.ForeignKey(ImagePost, on_delete=models.CASCADE, related_name='image_comment')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='image_comment')

    class Meta:
        db_table = 'image_comment'

# TODO post comment 추가 예정