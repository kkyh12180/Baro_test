from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView
from datetime import datetime

from search.search_in_elastic import *
from search.models import *

import string
import random

# Create your views here.
def main(request):
    user_pk = request.user.pk
    log_list = Prompt_log.objects.filter(user_id=user_pk).order_by('-created_at')[:15]
    context={'log_list':log_list}
    if request.method == 'POST':
        prompt=request.POST.get('prompt','')
        negative_prompt = request.POST.get('negative_prompt','')
        prompt, negative_prompt = tokenizer(prompt,negative_prompt)
        if user_pk:
            prompt_log_check=Prompt_log.objects.filter(user_id=user_pk,prompt=prompt,negative_prompt=negative_prompt)
            if not prompt_log_check:
                plid = ""
                while(True):
                    letters_set = string.ascii_letters
                    num = random.randrange(1,9)
                    random_list = random.sample(letters_set,num)
                    random_str = f"PL{''.join(random_list)}"
                    try :
                        Prompt_log.objects.get(prompt_log_id=random_str)
                    except:
                        plid=random_str
                        break
                Prompt_log.objects.create(prompt_log_id=plid,user_id=user_pk,prompt=prompt,negative_prompt=negative_prompt)
            else:
                prompt_log_check[0].created_at=datetime.now()
                prompt_log_check[0].save()
        context=result(prompt=prompt,negative_prompt=negative_prompt)
        return render(request,'search/main.html',context)
    return render(request,'search/main.html',context)

def delete_all(request):
    user_pk=request.user.pk
    log_list = Prompt_log.objects.filter(user_id=user_pk)
    for log in log_list:
        log.delete()
    return redirect('search:home')

def delete(request, pk):
    user_pk=request.user.pk
    log_list = Prompt_log.objects.filter(user_id=user_pk,prompt_log_id=pk)
    for log in log_list:
        log.delete()
    return redirect('search:home')

def result(prompt,negative_prompt):
    query_maker=QueryMake()
    data_list=query_maker.query_to_elastic(prompt,negative_prompt)
    context={'data_list':data_list}
    return context

class LogListView(ListView):
    model = Prompt_log
    context_object_name = 'log_list'
    template_name = 'search/log.html'
    paginate_by = 20

    def get_queryset(self):
        user_pk = self.request.user.pk
        queryset = Prompt_log.objects.filter(user_id=user_pk).order_by('-created_at')
        return queryset

def tokenizer(prompt,negative_prompt):
    #positive
    prompt=re.sub(r'[()\[\]{}]',',',prompt)
    tok = prompt.split(',')
    temp_prompt = ""
    for tk in tok:
        tk=make_tokenizer(tk)
        if not tk:
            continue
        if "<" in tk or ">" in tk :
            continue
        if temp_prompt:
            temp_prompt=temp_prompt+","+tk
        else :
            temp_prompt=tk
        prompt = Prompt.objects.filter(prompt=tk)
        if not prompt:
            prompt=Prompt()
            prompt.prompt=tk
            prompt.positive_weight=1
            prompt.save()
        else:
            prompt_temp = prompt[0]
            prompt_temp.positive_weight=prompt_temp.positive_weight+1
            prompt_temp.save()

    #negative
    negative_prompt = re.sub(r'[()\[\]{}]',',',negative_prompt)
    tok = negative_prompt.split(',')
    temp_negative_prompt = ""
    for tk in tok:
        tk=make_tokenizer(tk)
        if not tk:
            continue
        if "<" in tk or ">" in tk :
            continue
        if temp_negative_prompt:
            temp_negative_prompt=temp_negative_prompt+","+tk
        else :
            temp_negative_prompt=tk
        prompt = Prompt.objects.filter(prompt=tk)
        if not prompt:
            prompt=Prompt()
            prompt.prompt=tk
            prompt.negative_weight=1
            prompt.save()
        else:
            prompt_temp = prompt[0]
            prompt_temp.negative_weight=prompt_temp.negative_weight+1
            prompt_temp.save()
    return temp_prompt, temp_negative_prompt

def make_tokenizer(tk):
    if ":" in tk:
        i=tk.find(":")
        tk=tk[:i]
    return tk.strip()