from django import forms
from account.models import User
from django.contrib.auth.forms import UserCreationForm
import base64

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['user_id', 'e_mail','username', 'password1','password2']
        widgets = {'user_id': forms.HiddenInput()}

class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['e_mail', 'username', 'profile']

    profile = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['e_mail'].disabled = True

    def clean_profile(self):
        image = self.cleaned_data.get('profile')
        if image:
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
    
class AccountPasswordUpdateForm(UserCreationForm) :
    class Meta:
        model = User
        fields = ['password1','password2']