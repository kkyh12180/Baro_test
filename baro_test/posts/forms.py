from django.forms import ModelForm
from django import forms

from posts.models import Post

class PostCreationForm(ModelForm): 
    class Meta:
        model = Post
        fields = ['title','content','subscribe_only','project']