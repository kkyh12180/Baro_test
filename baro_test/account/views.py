from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.edit import FormMixin
from django.contrib import auth
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from account.decorators import account_ownership_required
from django.db import connection
from django.shortcuts import get_object_or_404

import string
import random

from account.forms import RegisterForm, AccountUpdateForm, AccountPasswordUpdateForm
from account.models import User
from follows.models import *
from comments.forms import CommentCreationForm
from channel.models import ChannelPost

has_ownership = [account_ownership_required, login_required]

# Create your views here.
def test(request) :
    return render(request, 'account/test.html')

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
        user=self.request.user
        if user.is_authenticated:
            subscription=SubscribeUploader.objects.filter(user=user,uploader=uploader)
            following=FollowUploader.objects.filter(user=user,uploader=uploader)
        else:
            subscription=None
            following=None
        context["subscription"]=subscription
        context["following"]=following
        image_post_list=ImagePost.objects.filter(user=uploader)
        context["object_list"]=image_post_list
        not_subscribe_image_list = image_post_list.filter(subscribe_only=False)
        context["not_subscribe_image_list"]=not_subscribe_image_list
        post_list=ChannelPost.objects.filter(user=uploader)
        context["post_list"]=post_list
        not_subscribe_post_list = post_list.filter(subscribe_only=False)
        context["not_subscribe_post_list"]=not_subscribe_post_list
        return context

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
        username=self.kwargs['username']
        return reverse_lazy('account:detail', kwargs={'username': username})

    def form_valid(self, form) :
        form.save()
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
    success_url = reverse_lazy('account:test')
    template_name = 'account/mypage.html'