from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView

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
        
        #Image_comment 생성
        temp_image_comment = ImageComment()
        temp_image_comment.comment=temp_comment
        temp_image_comment.image_post=ImagePost.objects.get(pk=self.request.POST['post_pk'])
        temp_image_comment.save()

        return super().form_valid(form)
    
    def get_success_url(self):
        image_coms = self.object.image_comment.all()
        image_com=image_coms[0]
        return reverse('images:detail',kwargs={'pk':image_com.image_post.pk})

@method_decorator(comment_ownership_required,'get')
@method_decorator(comment_ownership_required,'post')
class CommentDeleteView(DeleteView):
    model = Comment
    context_object_name = 'target_comment'
    template_name = 'comments/delete.html'

    def get_success_url(self):
        image_coms = self.object.image_comment.all()
        image_com=image_coms[0]
        return reverse('images:detail',kwargs={'pk':image_com.image_post.pk})