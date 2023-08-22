from typing import Any, Iterator
from django import forms
from accounts.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import django.contrib.auth.forms as auth_forms
from django.core.exceptions import ValidationError
from accounts.models import User

import os
from datetime import date

from synology_api import filestation
from search.pocket import pocket

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

class CustomPasswordResetForm(auth_forms.PasswordResetForm) :
    def clean(self) :
        cleaned_data = super().clean()
        e_mail = cleaned_data.get("email")

        # 유저 존재 체크
        user = User.objects.filter(e_mail=e_mail)

        if not user :
            raise ValidationError("사용자의 이메일 주소가 존재하지 않습니다.")
        
    def get_users(self, email=''):
        e_mail = self.cleaned_data.get('email')
        active_users = User.objects.filter(e_mail=e_mail)
        return (
            u for u in active_users
            if u.has_usable_password()
        )