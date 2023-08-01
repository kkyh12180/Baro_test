from django.forms import ModelForm
from django import forms

from posts.models import Post, Project

class PostCreationForm(ModelForm):
    project = forms.ModelChoiceField(queryset=Project.objects.exclude(project_id__in=['Announce']))

    class Meta:
        model = Post
        fields = ['title','content','subscribe_only','project']