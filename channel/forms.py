from django.forms import ModelForm
from django import forms

from channel.models import ChannelPost

class ChannelCreationForm(ModelForm):
    class Meta:
        model = ChannelPost
        fields = ['title','content', 'subscribe_only']