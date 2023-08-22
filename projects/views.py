from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from posts.models import Post
from projects.models import *
from projects.forms import *

import string
import random
# Create your views here.

#새로운 게시판 생성은 admin 계정만 진행할 수 있다.
@method_decorator(staff_member_required(login_url='admin:login'), name='dispatch')
class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectCreationForm
    template_name = 'projects/create.html'
    
    def form_valid(self, form):
        temp_post=form.save(commit=False)
        temp_post.user = self.request.user

        # Project_ID PK 처리
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

#각 게시판이 가지는 글의 정보가 표시된다.
class ProjectDetailView(ListView):
    model = Post
    context_object_name = 'post_list'
    template_name = 'projects/list.html'
    paginate_by = 20

    #project에 해당하는 post를 시간 역순으로 가져오는 코드
    def get_queryset(self):
        project_id = self.kwargs['pk']
        project = Project.objects.get(pk=project_id)
        project_list = Post.objects.filter(project=project).order_by('-post_time')
        return project_list
    
    #post에 project의 리스트와 현재 project를 html에 전달
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project_list = Project.objects.values('pk', 'title')
        context["project_list"] = project_list
        project_id = self.kwargs['pk']
        project = Project.objects.get(pk=project_id)
        context["target_project"] = project
        return context

#새로운 게시판 삭제는 admin 계정만 진행할 수 있다.
@method_decorator(staff_member_required(login_url='admin:login'), name='dispatch')
class ProjectDeleteView(DeleteView):
    model = Project
    context_object_name = "target_project"
    template_name = 'projects/list.html'

    def get_success_url(self):
        return reverse('projects:list',kwargs={'pk':'A_Announce'})
