from django import forms
from account.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os

from synology_api import filestation

PROFILE_URL = "https://vanecompany.synology.me/ai_image/user/"

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
        fl = filestation.FileStation('14.45.111.226', '5000', 'vane23', 'Syn_vane2023', secure=False, cert_verify=False, dsm_version=7, debug=True, otp_code=None)
        uid = self.cleaned_data.get('user_id')
        print(uid)
        image = self.cleaned_data.get('profile')
        if image:
            ext = image.name.split('.')[-1]
            image.name = f"{uid}.{ext}"
            path = default_storage.save(f"tmp/{image.name}", ContentFile(image.read()))
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            fl.upload_file(f"/web/ai_image/user", tmp_file)
            os.remove(tmp_file)
            self.cleaned_data['profile_image'] = f"{PROFILE_URL}{uid}.{ext}"
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