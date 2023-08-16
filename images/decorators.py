from django.http import HttpResponseForbidden
from images.models import ImagePost
from follows.models import SubscribeUploader

def image_post_ownership_required(func) :
    def decorated(request, *args, **kwargs) :
        image_post = ImagePost.objects.get(pk=kwargs['pk'])
        if not image_post.user == request.user :
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
        
    return decorated

def image_get_required(func):
    def decorated(request, *args, **kwargs):
        image_post = ImagePost.objects.get(pk=kwargs['pk'])
        user = request.user
        uploader = image_post.user
        if image_post.subscribe_only :
            if not SubscribeUploader.objects.filter(user=user,uploader=uploader):
                return HttpResponseForbidden()
        if image_post.adult:
            if not user.is_adult :
                return HttpResponseForbidden()
        return func(request,*args, **kwargs)
    
    return decorated