from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, RedirectView, DeleteView, ListView
from django.views.generic.list import MultipleObjectMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from posts.models import Post
from projects.decorators import *
from projects.forms import *
from projects.models import *
from follows.models import SubscribeUploader

import string
import random
# Create your views here.

@method_decorator(login_required,'get')
@method_decorator(login_required,'post')
@method_decorator(staff_member_required(login_url='admin:login'), name='dispatch')
class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectCreationForm
    template_name = 'projects/create.html'
    
    def form_valid(self, form):
        temp_post=form.save(commit=False)
        temp_post.user = self.request.user

        gid = ""
        while (True) :
            letters_set = string.ascii_letters
            num = random.randrange(1, 10) # 1부터 9 사이의 난수 생성
            random_list = random.sample(letters_set, num)
            random_str = f"G{''.join(random_list)}"

            try :
                Project.objects.get(project_id=random_str)
            except :
                gid = random_str
                temp_post.project_id = gid
                temp_post.save()
                break
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('projects:list',kwargs={'pk':self.object.pk})

class ProjectDetailView(ListView):
    model = Post
    context_object_name = 'post_list'
    template_name = 'projects/list.html'
    paginate_by = 20

    def get_queryset(self):
        project_id = self.kwargs['pk']
        project = Project.objects.get(pk=project_id)
        project_list = Post.objects.filter(project=project).order_by('-post_time')
        return project_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project_list = Project.objects.values('pk', 'title')
        context["project_list"] = project_list
        project_id = self.kwargs['pk']
        project = Project.objects.get(pk=project_id)
        context["target_project"] = project
        return context

@method_decorator(staff_member_required(login_url='admin:login'), name='dispatch')
class ProjectDeleteView(DeleteView):
    model = Project
    context_object_name = "target_project"
    template_name = 'projects/list.html'

    def get_success_url(self):
        return reverse('projects:list',kwargs={'pk':'A_Announce'})
