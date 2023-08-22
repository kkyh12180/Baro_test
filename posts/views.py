from django.urls import reverse
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, RedirectView
from django.views.generic.edit import FormMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404

from posts.decorators import *
from posts.models import *
from posts.forms import *
from comments.forms import CommentCreationForm

import string
import random

#글을 작성하기 위해서는 로그인이 필수이다.
@method_decorator(login_required,'get')
@method_decorator(login_required,'post')
class PostCreateView(CreateView):
    model = Post
    form_class = PostCreationForm
    template_name = 'posts/create.html'

    def form_valid(self, form):
        temp_post=form.save(commit=False)

        # UID 연결
        temp_post.user = self.request.user

        # Post_ID PK 처리
        pid = ""
        while (True) :
            letters_set = string.ascii_letters
            num = random.randrange(1, 10) # 1부터 9 사이의 난수 생성
            random_list = random.sample(letters_set, num)
            random_str = f"B{''.join(random_list)}"

            try :
                Post.objects.get(post_id=random_str)
            except :
                pid = random_str
                break
        temp_post.post_id = pid
        temp_post.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post:detail',kwargs={'pk':self.object.pk})
    
#공지사항 작성은 admin 계정만 진행할 수 있다.
@method_decorator(staff_member_required(login_url='admin:login'), name='dispatch')
class AnnounceCreateView(CreateView):
    model = Post
    form_class = AnnounceCreationForm
    template_name = 'posts/announce.html'

    def form_valid(self, form):
        temp_post=form.save(commit=False)
        temp_post.user = self.request.user
        temp_post.project = Project.objects.get(project_id="A_Announce")

        pid = ""
        while (True) :
            letters_set = string.ascii_letters
            num = random.randrange(1, 10) # 1부터 9 사이의 난수 생성
            random_list = random.sample(letters_set, num)
            random_str = f"B{''.join(random_list)}"

            try :
                Post.objects.get(post_id=random_str)
            except :
                pid = random_str
                break
        temp_post.post_id = pid
        temp_post.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post:detail',kwargs={'pk':self.object.pk})

#글의 상세 정보가 표시된다.
class PostDetailView(DetailView, FormMixin):
    model = Post
    form_class = CommentCreationForm
    context_object_name = 'target_post'
    template_name = 'posts/detail.html'

    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        post = self.object
        user = self.request.user

        if user.is_authenticated :
            likes = PostLike.objects.filter(user=user, post=post)
            context['likes'] = likes
        return context

#글을 작성한 유저는 글을 수정할 권한이 생긴다.
@method_decorator(post_ownership_required,'get')
@method_decorator(post_ownership_required,'post')
class PostUpdateView(UpdateView):
    model = Post
    form_class = PostCreationForm
    context_object_name = 'target_post'
    template_name = 'posts/update.html'

    def get_success_url(self):
        return reverse('post:detail',kwargs={'pk':self.object.pk})
    
#공지사항 수정은 admin 계정만 진행할 수 있다.
@method_decorator(staff_member_required(login_url='admin:login'), name='dispatch')
class AnnounceUpdateView(UpdateView):
    model = Post
    form_class = AnnounceCreationForm
    context_object_name = 'target_post'
    template_name = 'posts/announce_update.html'

    def get_success_url(self):
        return reverse('post:detail',kwargs={'pk':self.object.pk})

#글을 작성한 유저는 글을 삭제할 권한이 생긴다.
@method_decorator(post_ownership_required,'get')
@method_decorator(post_ownership_required,'post')
class PostDeleteView(DeleteView):
    model = Post
    context_object_name = 'target_post'
    template_name = 'posts/detail.html'

    def get_success_url(self):
        return reverse('projects:list',kwargs={'pk':'A_Announce'})

#게시글에 좋아요를 할  수 있다. 이 좋아요 상태이면 해제가 된다.
class PostLikeView(RedirectView) :
    def get_redirect_url(self, *args, **kwargs) :
        return reverse('post:detail', kwargs={'pk': self.request.GET.get('post_pk')})
    
    def get(self, request, *args, **kwargs) :
        post = get_object_or_404(Post, pk=self.request.GET.get('post_pk'))
        user = self.request.user
        like = PostLike.objects.filter(user=user, post=post)

        if like.exists() :
            post.like_number -= 1
            post.save()
            like.delete()
        else :
            post.like_number += 1
            post.save()
            PostLike(user=user, post=post).save()

        return super(PostLikeView, self).get(request, *args, **kwargs)