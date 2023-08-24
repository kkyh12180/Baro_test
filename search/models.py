from django.db import models
from accounts.models import User

# Create your models here.
class Prompt(models.Model):
    prompt = models.CharField(primary_key=True,max_length=255)
    positive_weight = models.IntegerField(default=0)
    negative_weight = models.IntegerField(default=0)

    class Meta:
        db_table = 'prompt'

class Prompt_log(models.Model):
    prompt_log_id = models.CharField(primary_key=True,max_length=10)
    user = models.ForeignKey(User,on_delete=models.CASCADE, blank=True, null=True, related_name="prompt_log")
    prompt = models.TextField()
    negative_prompt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prompt_log'

class Prompt_rank(models.Model):
    rank = models.IntegerField(primary_key=True)
    prompt = models.TextField()
    negative_prompt = models.TextField()

    class Meta:
        db_table = 'prompt_rank'