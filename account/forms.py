from django import forms
from account.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os

from synology_api import filestation
from search.pocket import pocket
from datetime import date

PROFILE_URL = "https://vanecompany.synology.me/ai_image/user/"
info = pocket()
fl = filestation.FileStation(info.nas_host, info.nas_port, info.nas_id, info.nas_password, secure=False, cert_verify=False, dsm_version=7, debug=True, otp_code=None)

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['user_id', 'e_mail','username', 'birthday', 'password1','password2']
        widgets = {'user_id': forms.HiddenInput()}

    birthday = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def save(self, commit=True) :
        instance = super().save(commit=False)
        
        # 성인 처리
        birthdate = self.cleaned_data.get('birthday', '')
        today = date.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        if (age < 18) :
            instance.is_adult = False
        else :
            instance.is_adult = True

        if commit:
            instance.save()
        return instance

class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['e_mail', 'username', 'birthday', 'profile']

    profile = forms.ImageField(required=False)
    birthday = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['e_mail'].disabled = True

    def clean_profile(self):
        uid = self.cleaned_data.get('username')
        image = self.cleaned_data.get('profile')
        if image:
            ext = "png"
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

        # 성인 처리
        birthdate = self.cleaned_data.get('birthday', '')
        today = date.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        if (age < 18) :
            instance.is_adult = False
        else :
            instance.is_adult = True

        if commit:
            instance.save()
        return instance
    
class AccountPasswordUpdateForm(UserCreationForm) :
    class Meta:
        model = User
        fields = ['password1','password2']