from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.views.generic.edit import FormMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


from posts.forms import *
from posts.models import *
from posts.decorators import *
from comments.forms import CommentCreationForm
# Create your views here.

import string
import random

@method_decorator(login_required,'get')
@method_decorator(login_required,'post')
class PostCrateView(CreateView):
    model = Post
    form_class = PostCreationForm
    template_name = 'posts/create.html'

    def form_valid(self, form):
        temp_post=form.save(commit=False)
        temp_post.user = self.request.user

        pid = ""
        while (True) :
            letters_set = string.ascii_letters
            num = random.randrange(1, 10) # 1부터 9 사이의 난수 생성
            random_list = random.sample(letters_set, num)
            random_str = f"P{''.join(random_list)}"

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
    
class PostDetailView(DetailView, FormMixin):
    model = Post
    form_class = CommentCreationForm
    context_object_name = 'target_post'
    template_name = 'posts/detail.html'

@method_decorator(post_ownership_required,'get')
@method_decorator(post_ownership_required,'post')
class PostUpdateView(UpdateView):
    model = Post
    form_class = PostCreationForm
    context_object_name = 'target_post'
    template_name = 'posts/update.html'

    def get_success_url(self):
        return reverse('post:detail',kwargs={'pk':self.object.pk})


@method_decorator(post_ownership_required,'get')
@method_decorator(post_ownership_required,'post')
class PostDeleteView(DeleteView):
    model = Post
    context_object_name = 'target_post'
    success_url = reverse_lazy('post:list')
    template_name = 'posts/delete.html'

class PostListView(ListView):
    model = Post
    context_object_name = 'post_list'
    template_name = 'posts/list.html'
    ordering = ['-post_time']
    paginate_by = 25

def clear(request):
    posts=Post.objects.all()
    for post in posts:
        post.delete()
    return reverse('post:list')
    