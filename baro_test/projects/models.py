from django.db import models

# Create your models here.

class Project(models.Model) : 
    # TODO project_id는 G로 시작해야함! 로직 수정 때 확인
    project_id = models.CharField(primary_key=True, max_length=10)
    image = models.ImageField(upload_to='project/', null=False)
    title = models.CharField(max_length=20, null=False)
    description = models.CharField(max_length=200, null=True)
    project_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project'