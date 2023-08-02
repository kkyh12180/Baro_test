from django.db import models

# Create your models here.
class Prompt(models.Model):
    prompt = models.CharField(primary_key=True,max_length=100)
    positive_weight = models.IntegerField(default=0)
    negative_weight = models.IntegerField(default=0)

    class Meta:
        db_table = 'prompt'