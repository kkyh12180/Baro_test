from django.forms import ModelForm
from projects.models import Project
from django import forms
import base64

class ProjectCreationForm(ModelForm):
    class Meta:
        model=Project
        fields = ['title','description','profile']

    profile = forms.ImageField(required=False)

    def clean_profile(self):
        image = self.cleaned_data.get('profile')
        if image :
            content = image.read()
            image_binary = base64.b64encode(content).decode('UTF-8')
            self.cleaned_data['profile_image'] = image_binary
        return image

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.profile_image = self.cleaned_data.get('profile_image', '')
        if commit:
            instance.save()
        return instance
    