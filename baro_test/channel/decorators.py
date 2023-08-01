from django.http import HttpResponseForbidden
from channel.models import *

def channel_ownership_required(func):
    def decorated(request,*args, **kwargs):
        post=ChannelPost.objects.get(pk=kwargs['pk'])
        if not post.user==request.user:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return decorated

