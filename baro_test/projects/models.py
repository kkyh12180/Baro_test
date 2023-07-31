from django.db import models
from account.models import User
# Create your models here.

class Project(models.Model) : 
    # TODO project_id는 G로 시작해야함! 로직 수정 때 확인
    project_id = models.CharField(primary_key=True, max_length=10)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='project')
    profile_image = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=20, null=False)
    description = models.CharField(max_length=200, null=True)
    project_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project'