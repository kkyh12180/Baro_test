from django.db import models
from accounts.models import User
# Create your models here.

class Project(models.Model) : 
    project_id = models.CharField(primary_key=True, max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='project')
    title = models.CharField(max_length=20, null=False, unique=True)
    description = models.CharField(max_length=200, null=True)
    project_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project'

    def __str__(self):
        return f'{self.title}'