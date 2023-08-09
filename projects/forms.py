from django.forms import ModelForm
from projects.models import Project
from django import forms
import base64

class ProjectCreationForm(ModelForm):
    class Meta:
        model=Project
        fields = ['title','description']

    