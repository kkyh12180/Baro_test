from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, RedirectView, DeleteView, ListView
from django.views.generic.list import MultipleObjectMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

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
class ProjectCrateView(CreateView):
    model = Project
    form_class = ProjectCreationForm
    template_name = 'projects/create.html'
    
    def form_valid(self, form):
        temp_post=form.save(commit=False)
        temp_post.user = self.request.user
        while True:
            temp_project=Project.objects.filter(title=temp_post.title)
            if not temp_project.exists():
                break
            temp_post.title=temp_post.title+"l"
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
        return reverse('projects:detail',kwargs={'pk':self.object.pk})


class ProjectSetView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        temp = Project()
        temp.project_id="Atemp"
        temp.user = self.request.user
        temp.title = "자유게시판"
        temp.save()
        Announce = Project()
        Announce.project_id="Announce"
        Announce.user = self.request.user
        Announce.title = "공지사항"
        Announce.save()
        voc = Project()
        voc.project_id="Avoc"
        voc.user = self.request.user
        voc.title = "VOC"
        voc.save()
        return reverse('projects:list')

class ProjectDetailView(DetailView, MultipleObjectMixin):
    model = Project
    context_object_name = 'target_project'
    template_name = 'projects/detail.html'
    paginate_by = 25 

    def get_context_data(self, **kwargs):
        if self.object.pk == "Atemp":
            object_list=Post.objects.filter(project=None)
        else:
            object_list=Post.objects.filter(project=self.get_object())
        '''not_subscribe_list=object_list.filter(subscribe_only=False)
        subscribe_list=object_list.filter(subscribe_only=True)

        self_list=[post for post in subscribe_list if self.request.user == post.user]

        set_list = [post for post in subscribe_list if SubscribeUploader.objects.filter(user=self.request.user,uploader=post.user)]

        object_list=list(not_subscribe_list)+set_list+self_list
        sorted_object_list = sorted(object_list, key=lambda post: post.post_time, reverse=True)'''
        return super(ProjectDetailView,self).get_context_data(object_list=object_list,**kwargs)

class ProjectListView(ListView, MultipleObjectMixin):
    model = Project
    context_object_name = 'project_list'
    template_name = 'projects/list.html'
    paginate_by = 25
    
    '''def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["announce_list"] = 
        return context
    
    def get(self, request, *args, **kwargs):
        announce_project=Project.objects.get(pk="Announce")
        temp_project=Project.objects.get(pk="Atemp")
        voc_project=Project.objects.get(pk="Avoc")
        object_list=Post.objects.get(project=announce_project)
        return super().get(request, *args, **kwargs)'''
    

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
