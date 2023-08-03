from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, RedirectView

from search.search_in_elastic import *
from search.models import *

# Create your views here.
def main(request):
    if request.method == 'POST':
        prompt=request.POST.get('prompt','')
        negative_prompt = request.POST.get('negative_prompt','')
        print(request.user.pk)
        user_pk=request.user.pk
        if user_pk:
            count=Prompt_log.objects.filter(user_id=user_pk).count()
            log_id = str(user_pk)+str(count)
            Prompt_log.objects.create(prompt_log_id=log_id,user_id=user_pk,prompt=prompt,negative_prompt=negative_prompt)
        context=result(prompt=prompt,negative_prompt=negative_prompt)
        return render(request,'search/result.html',context)
    return render(request,'search/main.html')

def result(prompt,negative_prompt):
    query_maker=QueryMake()
    data_list=query_maker.query_to_elastic(prompt,negative_prompt)
    context={'data_list':data_list}
    return context

class LogListView(ListView):
    model = Prompt_log
    context_object_name = 'log_list'
    template_name = 'search/log.html'
    paginate_by = 25

    def get_queryset(self):
        user_pk = self.request.user.pk
        queryset = Prompt_log.objects.filter(user_id=user_pk).order_by('-created_at')
        return queryset

def research(request, pk):
    log = Prompt_log.objects.get(pk=pk)
    context=result(prompt=log.prompt,negative_prompt=log.negative_prompt)
    return render(request,'search/result.html',context)

def test(request):
    return render(request,'search/main.html')