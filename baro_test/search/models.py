from django.db import models
from account.models import User

# Create your models here.
class Prompt(models.Model):
    prompt = models.CharField(primary_key=True,max_length=100)
    positive_weight = models.IntegerField(default=0)
    negative_weight = models.IntegerField(default=0)

    class Meta:
        db_table = 'prompt'

class Prompt_log(models.Model):
    prompt_log_id = models.CharField(primary_key=True,max_length=12)
    user = models.ForeignKey(User,on_delete=models.CASCADE, blank=True, null=True, related_name="prompt_log")
    prompt = models.TextField()
    negative_prompt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prompt_log'