from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, RedirectView

from follows.models import *

# Create your views here.
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

class SubscriptionListView(ListView):
    model = ImagePost
    context_object_name = "image_post_list"
    template_name="follows/list.html"
    paginate_by = 20

    def get_queryset(self):
        writes=SubscribeUploader.objects.filter(user=self.request.user).values_list('uploader')
        subscribed_posts = ImagePost.objects.filter(user__in=writes)
        return subscribed_posts.filter(subscribe_only=True).order_by('-post_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        uploader_ids = SubscribeUploader.objects.filter(user=self.request.user).values_list('uploader')
        context["user_list"] = User.objects.filter(pk__in=uploader_ids)
        return context
    
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
        writes = FollowUploader.objects.filter(user=self.request.user).values_list('uploader')
        subscribed_posts = ImagePost.objects.filter(user__in=writes)
        return subscribed_posts.filter(subscribe_only=False).order_by('-post_time')
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
        bookmarked_posts = BookmarkImagePost.objects.filter(user=self.request.user).values_list('image_post').order_by('-bookmark_time')
        bookmark_list=[]
        for bookmarked_post in bookmarked_posts:
            bookmark_list.append(ImagePost.objects.get(pk=bookmarked_post[0]))
        return bookmark_list