from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.views.generic.list import MultipleObjectMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from posts.models import Post
from projects.decorators import *
from projects.forms import *
from projects.models import *

import string
import random
# Create your views here.

@method_decorator(login_required,'get')
@method_decorator(login_required,'post')
class ProjectCrateView(CreateView):
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
                break
        temp_post.project_id = gid
        temp_post.save()

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('projects:detail',kwargs={'pk':self.object.pk})
    
class ProjectDetailView(DetailView, MultipleObjectMixin):
    model = Project
    context_object_name = 'target_project'
    template_name = 'projects/detail.html'
    paginate_by = 25
    def get_context_data(self, **kwargs):
        object_list=Post.objects.filter(project=self.get_object())
        return super(ProjectDetailView,self).get_context_data(object_list=object_list,**kwargs)

class ProjectListView(ListView):
    model = Project
    context_object_name = 'project_list'
    template_name = 'projects/list.html'
    paginate_by = 25

class ProjectDeleteView(DeleteView):
    model = Project
    context_object_name = "target_project"
    template_name = 'projects/delete.html'
    def get_success_url(self):
        return reverse('projects:list')
def clear(request):
    projects=Project.objects.all()
    for project in projects:
        if not project.pk:
            project.delete()