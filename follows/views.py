from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, RedirectView

from follows.models import *

#유저를 구독 상태면 해제, 아니면 구독
@method_decorator(login_required,'get')
class SubscriptionView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('account:detail',kwargs={'username':self.request.GET.get('account_pk')})
    def get(self,request,*args,**kwargs):
        uploader=get_object_or_404(User,username=self.request.GET.get('account_pk'))
        user=self.request.user

        subscription = SubscribeUploader.objects.filter(user=user,uploader=uploader)
        if subscription.exists():
            subscription.delete()
        else:
            SubscribeUploader(user=user,uploader=uploader).save()
        return super(SubscriptionView,self).get(request,*args, **kwargs)

#구독한 사람의 작품을 확인
class SubscriptionListView(ListView):
    model = ImagePost
    context_object_name = "image_post_list"
    template_name="follows/list.html"
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        try:
            user_adult = user.is_adult
        except:
            user_adult=False
        
        #구독한 사람의 구독자 전용 이미지 가져오기
        writes=SubscribeUploader.objects.filter(user=user).values_list('uploader')
        subscribed_posts = ImagePost.objects.filter(user__in=writes,subscribe_only=True)

        #user의 성인 설정에 따라 이미지 구분
        if user_adult:
            return subscribed_posts.order_by('-post_time')
        return subscribed_posts.filter(adult=False).order_by('-post_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        uploader_ids = SubscribeUploader.objects.filter(user=self.request.user).values_list('uploader')
        context["user_list"] = User.objects.filter(pk__in=uploader_ids)
        return context

#유저를 팔로우 상태면 해제, 아니면 팔로우
@method_decorator(login_required,'get')
class FollowView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('account:detail',kwargs={'username':self.request.GET.get('account_pk')})
    def get(self,request,*args,**kwargs):
        uploader=get_object_or_404(User,username=self.request.GET.get('account_pk'))
        user=self.request.user

        subscription = FollowUploader.objects.filter(user=user,uploader=uploader)
        if subscription.exists():
            subscription.delete()
        else:
            FollowUploader(user=user,uploader=uploader).save()
        return super(FollowView,self).get(request,*args, **kwargs)

class FollowingListView(ListView):
    model=ImagePost
    context_object_name='image_post_list'
    template_name="follows/list.html"
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        try:
            user_adult = user.is_adult
        except:
            user_adult=False
        
        #팔로운한 사람의 구독자 전용 이미지 가져오기
        writes = FollowUploader.objects.filter(user=user).values_list('uploader')
        subscribed_posts = ImagePost.objects.filter(user__in=writes,subscribe_only=False)
        
        #user의 성인 설정에 따라 이미지 구분
        if user_adult:
            return subscribed_posts.order_by('-post_time')
        return subscribed_posts.filter(adult=False).order_by('-post_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        uploader_ids = FollowUploader.objects.filter(user=self.request.user).values_list('uploader')
        context["user_list"] = User.objects.filter(pk__in=uploader_ids)
        return context

class BookmarkedListView(ListView):
    model=ImagePost
    context_object_name = "bookmark_list"
    template_name="follows/bookmark.html"
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        try:
            user_adult = user.is_adult
        except:
            user_adult=False
        
        #자신이 최근에 북마크 한 데이터 가져오기
        bookmarked_posts = BookmarkImagePost.objects.filter(user=user).order_by('-bookmark_time')
        bookmarked_image_posts = [bookmark.image_post for bookmark in bookmarked_posts]
        
        #북마크한 데이터의 성인 전용과 자신의 상태 비교 후 구분
        bookmark_list = [
            post for post in bookmarked_image_posts if post.adult == user_adult or not post.adult
        ]
        return bookmark_list