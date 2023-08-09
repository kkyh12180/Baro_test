from django.http import HttpResponseForbidden
from images.models import ImagePost

def image_post_ownership_required(func) :
    def decorated(request, *args, **kwargs) :
        image_post = ImagePost.objects.get(pk=kwargs['pk'])
        if not image_post.user == request.user :
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
        
    return decorated