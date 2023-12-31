from django.http import HttpResponseForbidden
from channel.models import *
from follows.models import SubscribeUploader

def channel_ownership_required(func):
    def decorated(request,*args, **kwargs):
        post=ChannelPost.objects.get(pk=kwargs['pk'])
        if not post.user==request.user:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return decorated

#채널을 링크로 접속시 구독자 인지 여부 확인
def channel_get_required(func):
    def decorated(request, *args, **kwargs):
        image_post = ChannelPost.objects.get(pk=kwargs['pk'])
        user = request.user
        uploader = image_post.user
        if user==uploader:
            return func(request,*args, **kwargs)
        if image_post.subscribe_only :
            if not SubscribeUploader.objects.filter(user=user,uploader=uploader):
                return HttpResponseForbidden()
        return func(request,*args, **kwargs)
    
    return decorated