from django.forms.models import BaseModelForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, RedirectView
from django.shortcuts import get_object_or_404

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from comments.decorators import *
from comments.forms import *
from comments.models import *

import string
import random

class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentCreationForm
    template_name = 'comment/create.html'
    def form_valid(self, form):

        temp_comment = form.save(commit=False)

        # UID 연결
        temp_comment.user = self.request.user
        
        # CID PK 처리
        cid = ""
        while (True) :
            letters_set = string.ascii_letters
            num = random.randrange(1, 15) # 1부터 14 사이의 난수 생성
            random_list = random.sample(letters_set, num)
            random_str = f"C{''.join(random_list)}"

            try :
                Comment.objects.get(comment_id=random_str)
            except :
                cid = random_str
                break
        temp_comment.comment_id = cid
        temp_comment.save()
        temp_pk=self.request.POST['post_pk']

        #pk_id 파악
        if temp_pk[0]=="I":
            #Image_comment 생성
            temp_image_comment = ImageComment()
            temp_image_comment.comment=temp_comment
            temp_image_comment.image_post=ImagePost.objects.get(pk=temp_pk)
            temp_image_comment.save()
            return super().form_valid(form)
        
        if temp_pk[0]=="C":
            temp_channel_comment = ChannelPostComment()
            temp_channel_comment.comment=temp_comment
            temp_channel_comment.channel_post=ChannelPost.objects.get(pk=temp_pk)
            temp_channel_comment.save()
            return super().form_valid(form)
        else :
            #Post_comment 생성
            temp_post_comment = PostComment()
            temp_post_comment.comment=temp_comment
            temp_post_comment.post=Post.objects.get(pk=temp_pk)
            temp_post_comment.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        image_coms = self.object.image_comment.all()
        if image_coms:
            image_com=image_coms[0]
            return reverse('images:detail',kwargs={'pk':image_com.image_post.pk})
        
        channel_coms = self.object.channel_comment.all()
        if channel_coms:
            channel_com = channel_coms[0]
            return reverse('channel:detail',kwargs={'pk':channel_com.channel_post.pk})
        
        post_coms = self.object.post_comment.all()
        if post_coms:
            post_com=post_coms[0]
            return reverse('post:detail',kwargs={'pk':post_com.post.pk})

@method_decorator(comment_ownership_required,'get')
@method_decorator(comment_ownership_required,'post')
class CommentDeleteView(DeleteView):
    model = Comment
    context_object_name = 'target_comment'
    template_name = 'comments/delete.html'
    def get_success_url(self):
        image_coms = self.object.image_comment.all()
        if image_coms:
            image_com=image_coms[0]
            return reverse('images:detail',kwargs={'pk':image_com.image_post.pk})
        
        channel_coms = self.object.channel_comment.all()
        if channel_coms:
            channel_com = channel_coms[0]
            return reverse('channel:detail',kwargs={'pk':channel_com.channel_post.pk})
        
        post_coms = self.object.post_comment.all()
        if post_coms:
            post_com=post_coms[0]
            return reverse('post:detail',kwargs={'pk':post_com.post.pk})
        
        

    
class CommentImagePostLikeView(RedirectView) :
    def get_redirect_url(self, *args, **kwargs) :
        comment = get_object_or_404(Comment, pk=self.request.GET.get('comment_pk'))
        ptype = ""
        try :
            image_post = ImageComment.objects.get(comment=comment).image_post
            ptype = "ip"
            image_post_pk = image_post.image_post_id
            return reverse('images:detail', kwargs={'pk': image_post_pk})
        except :
            post = PostComment.objects.get(comment=comment).post
            ptype = "p"
            post_pk=post.post_id
            return reverse('post:detail', kwargs={'pk': post_pk})
    
    def get(self, request, *args, **kwargs) :
        comment = get_object_or_404(Comment, pk=self.request.GET.get('comment_pk'))
        user = self.request.user
        like = CommentLike.objects.filter(user=user, comment=comment)

        if like.exists() :
            like.delete()
        else :
            CommentLike(user=user, comment=comment).save()

        return super(CommentImagePostLikeView, self).get(request, *args, **kwargs)
    
