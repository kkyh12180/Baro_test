from typing import Any, Optional
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, RedirectView, ListView
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.edit import FormMixin
from django.contrib import auth
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from account.decorators import account_ownership_required
from django.db import connection
from django.shortcuts import get_object_or_404
from django.utils import translation

import string
import random

from django.utils.translation import gettext as _

from account.forms import RegisterForm, AccountUpdateForm, AccountPasswordUpdateForm
from account.models import User
from follows.models import *
from comments.forms import CommentCreationForm
from channel.models import ChannelPost
from search.pocket import pocket

from synology_api import filestation

has_ownership = [account_ownership_required, login_required]
PROFILE_URL = "https://vanecompany.synology.me/ai_image/user/"

info = pocket()
fl = filestation.FileStation(info.nas_host, info.nas_port, info.nas_id, info.nas_password, secure=False, cert_verify=False, dsm_version=7, debug=True, otp_code=None)


class AccountCreateView(CreateView) :
    model = User
    
    def get_initial(self) :
        cursor = connection.cursor()
        uid = ""
        while (True) :
            letters_set = string.ascii_letters
            num = random.randrange(1, 10) # 1부터 9 사이의 난수 생성
            random_list = random.sample(letters_set, num)
            random_str = f"U{''.join(random_list)}"

            post_list_sql = f'SELECT COUNT(*) FROM user WHERE user_id="{random_str}";'
            cursor.execute(post_list_sql)
            user_num = int(cursor.fetchone()[0])

            if (user_num == 0) : 
                uid = random_str
                break
        initial = super().get_initial()
        initial['user_id'] = uid
        return initial
    
    form_class = RegisterForm
    success_url = reverse_lazy('account:signin')
    template_name = 'account/signup.html'

class AccountDetailView(DetailView, FormMixin) :
    model = User
    form_class = CommentCreationForm
    context_object_name = 'target_user'
    template_name = 'account/mypage.html'
    paginate_by = 25
    
    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        return get_object_or_404(User,username=username)

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        uploader=self.object

        subscribe_list = uploader.subscriber.all()
        follow_list = uploader.follower.all()
        user=self.request.user

        if user.is_authenticated:
            subscription=subscribe_list.filter(user=user)
            following=follow_list.filter(user=user)
        else:
            subscription=None
            following=None
        
        context["follow_list"]=follow_list
        context["subscribe_list"]=subscribe_list

        context["subscription"]=subscription
        context["following"]=following

        user_image_post_list=ImagePost.objects.filter(user=uploader).order_by('-post_time')
        context["object_list"]=user_image_post_list[:15]

        post_list=ChannelPost.objects.filter(user=uploader).order_by('-post_time')
        context["post_list"]=post_list
        not_subscribe_post_list = post_list.filter(subscribe_only=False)
        context["not_subscribe_post_list"]=not_subscribe_post_list
        return context

class AccountImageListView(ListView):
    model = ImagePost
    context_object_name = 'image_post_list'
    template_name = 'images/list.html'
    paginate_by = 20
    
    def get_queryset(self):
        username=self.kwargs['username']
        user = User.objects.get(username=username)
        return ImagePost.objects.filter(user_id=user.pk,subscribe_only=False,adult=False).order_by('-post_time')

@method_decorator(has_ownership, 'get')
@method_decorator(has_ownership, 'post')
class AccountUpdateView(UpdateView) :
    model = User
    context_object_name = 'target_user'
    form_class = AccountUpdateForm
    template_name = 'account/edit_mypage.html'

    def get_initial(self) :
        initial = super().get_initial()
        initial['username'] = self.request.user.username
        return initial

    def get_success_url(self):
        uid=self.kwargs['pk']
        user=User.objects.get(user_id=uid)
        return reverse_lazy('account:detail', kwargs={'username': user.username})

    def form_valid(self, form) :
        temp_form = form.save()
        username = form.cleaned_data['username']
        initial_username = self.get_initial()['username']
        check = False
        if username != initial_username:
            username = initial_username
            check = True
        if not temp_form.profile_image or check:
            temp = fl.get_file_list("/web/ai_image/user")
            temp = temp["data"]["files"]
            path_to_delete="/web/ai_image/user/"+username+".png"
            try:
                fl.delete_blocking_function(path_to_delete)
                print(f"Deleted: {path_to_delete}")
            except Exception as e:
                print(f"An error occurred while deleting: {e}")
        return super().form_valid(form)
    
@method_decorator(has_ownership, 'get')
@method_decorator(has_ownership, 'post')
class AccountPasswordUpdateView(UpdateView) :
    model = User
    context_object_name = 'target_user'
    form_class = AccountPasswordUpdateForm
    template_name = 'account/edit_password.html'
    success_url = reverse_lazy('account:signin')

@method_decorator(has_ownership, 'get')
@method_decorator(has_ownership, 'post')
class AccountDeleteView(DeleteView) :
    model = User
    context_object_name = 'target_user'
    success_url = reverse_lazy('search:home')
    template_name = 'account/mypage.html'
    
    def post(self, request, *args, **kwargs):
        uid = self.kwargs['pk']
        user = User.objects.get(user_id = uid)
        path_to_delete="/web/ai_image/user/"+user.username+".png"
        try:
            fl.delete_blocking_function(path_to_delete)
            print(f"Deleted: {path_to_delete}")
        except Exception as e:
            print(f"An error occurred while deleting: {e}")
        return super().post(request, *args, **kwargs)

class ChangeLanguageView(RedirectView):
    permanent = False
    
    def get_redirect_url(self, *args, **kwargs):
        next_url = self.request.GET.get('next', '/')
        # 언어 prefix 변경
        if next_url.startswith('/en/'):
            next_url = '/ko/' + next_url[4:]
        elif next_url.startswith('/ko/'):
            next_url = '/en/' + next_url[4:]
        return next_url
