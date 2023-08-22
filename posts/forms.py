from django.forms import ModelForm
from django import forms

from posts.models import Post, Project

# 게시글을 작성할 때는 project를 선택하여야한다.
class PostCreationForm(ModelForm):
    #공지사항은 선택 할 수 없다.
    project = forms.ModelChoiceField(queryset=Project.objects.exclude(project_id__in=['A_Announce']))

    class Meta:
        model = Post
        fields = ['title','content', 'project']

# 공지사항은 일반적으로 작성이 불가능한 대신 project를 선택 안하는 form을 설정해주었다.
class AnnounceCreationForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title','content']