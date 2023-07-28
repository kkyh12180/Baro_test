from django.forms import ModelForm
from projects.models import Project

class ProjectCreationForm(ModelForm):
    class Meta:
        model=Project
        fields = ['title','description']