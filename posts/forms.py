from django.forms import ModelForm
from django import forms

from posts.models import Post, Project

class PostCreationForm(ModelForm):
    project = forms.ModelChoiceField(queryset=Project.objects.exclude(project_id__in=['A_Announce']))

    class Meta:
        model = Post
        fields = ['title','content', 'project']

class AnnounceCreationForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title','content']