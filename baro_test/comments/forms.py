from django.forms import ModelForm
from comments.models import *

class CommentCreationForm(ModelForm):
    class Meta:
        model=Comment
        fields=['content']