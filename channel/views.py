from django.urls import reverse
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, RedirectView
from django.views.generic.edit import FormMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from channel.decorators import *
from channel.models import *
from channel.forms import *
from comments.forms import CommentCreationForm

import string
import random

#채널에 글을 쓰기 위해 로그인은 필수
@method_decorator(login_required,'get')
@method_decorator(login_required,'post')
class ChannelCreateView(CreateView):
    model = ChannelPost
    form_class = ChannelCreationForm
    template_name = 'channel/create.html'

    def form_valid(self, form):
        temp_post=form.save(commit=False)
        temp_post.user = self.request.user

        #Channel_Post_ID 생성
        cid = ""
        while (True) :
            letters_set = string.ascii_letters
            num = random.randrange(1, 10) # 1부터 9 사이의 난수 생성
            random_list = random.sample(letters_set, num)
            random_str = f"H{''.join(random_list)}"

            try :
                ChannelPost.objects.get(channel_post_id=random_str)
            except :
                cid = random_str
                break
        temp_post.channel_post_id = cid
        temp_post.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('channel:detail',kwargs={'pk':self.object.pk})

#채널 detail에서 댓글 폼이 있어 댓글도 작성 가능
@method_decorator(channel_get_required, 'get')
class ChannelDetailView(DetailView, FormMixin):
    model = ChannelPost
    form_class = CommentCreationForm
    context_object_name = 'target_post'
    template_name = 'channel/detail.html'

    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        post = self.object
        user = self.request.user

        if user.is_authenticated :
            likes = ChannelPostLike.objects.filter(user=user, post=post)
            context['likes'] = likes
        return context

@method_decorator(channel_ownership_required,'get')
@method_decorator(channel_ownership_required,'post')
class ChannelUpdateView(UpdateView):
    model = ChannelPost
    form_class = ChannelCreationForm
    context_object_name = 'target_post'
    template_name = 'channel/update.html'

    def get_success_url(self):
        return reverse('channel:detail',kwargs={'pk':self.object.pk})

@method_decorator(channel_ownership_required,'get')
@method_decorator(channel_ownership_required,'post')
class ChannelDeleteView(DeleteView):
    model = ChannelPost
    context_object_name = 'target_post'
    template_name = 'channel/detail.html'

    def get_success_url(self) :
        username = self.request.user.username
        return reverse('account:detail', kwargs={'username':username})

class ChannelLikeView(RedirectView) :
    def get_redirect_url(self, *args, **kwargs) :
        return reverse('channel:detail', kwargs={'pk': self.request.GET.get('post_pk')})
    
    def get(self, request, *args, **kwargs) :
        post = get_object_or_404(ChannelPost, pk=self.request.GET.get('post_pk'))
        user = self.request.user
        like = ChannelPostLike.objects.filter(user=user, post=post)

        #좋아요가 눌러져있으면 해제 후 좋아요 수 감소, 아니면 반대로
        if like.exists() :
            post.like_number -= 1
            post.save()
            like.delete()
        else :
            ChannelPostLike(user=user, post=post).save()
            post.like_number += 1
            post.save()

        return super(ChannelLikeView, self).get(request, *args, **kwargs)
