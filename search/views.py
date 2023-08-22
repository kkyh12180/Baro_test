from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, View
from django.utils import timezone
from django.core.paginator import Paginator

from search.search_in_elastic import *
from search.models import *
from search.elastic import *
from search.pocket import pocket
from search.prompt_make import MakeImage
from images.models import *

import string
import random
# import openai

# openai.api_key = pocket().chat_key

class SearchListView(ListView):
    template_name = 'search/main.html'
    context_object_name = 'log_list'
    paginate_by = 10

    def get_queryset(self):
        user_pk = self.request.user.pk
        return Prompt_log.objects.filter(user_id=user_pk).order_by('-created_at')[:15]

    def post(self, request, *args, **kwargs):
        user_pk = request.user.pk
        prompt = request.POST.get('prompt', '')
        negative_prompt = request.POST.get('negative_prompt', '')
        prompt, negative_prompt = tokenizer(prompt, negative_prompt)

        if user_pk:
            prompt_log_check = Prompt_log.objects.filter(user_id=user_pk, prompt=prompt, negative_prompt=negative_prompt)

            if not prompt_log_check:
                plid = ""
                while True:
                    letters_set = string.ascii_letters
                    num = random.randrange(1, 10)
                    random_list = random.sample(letters_set, num)
                    random_str = f"L{''.join(random_list)}"
                    try:
                        Prompt_log.objects.get(prompt_log_id=random_str)
                    except Prompt_log.DoesNotExist:
                        plid = random_str
                        break

                Prompt_log.objects.create(prompt_log_id=plid, user_id=user_pk, prompt=prompt, negative_prompt=negative_prompt)
            else:
                prompt_log_check[0].created_at = timezone.now()
                prompt_log_check[0].save()
        
        # Store the search results in the session
        request.session['search_query'] = {'prompt': prompt, 'negative_prompt': negative_prompt}
        
        # Build the URL for redirecting with pagination
        redirect_url = reverse('search:result')
        redirect_url += f'?page=1'
        
        # Redirect to ResultView with pagination
        return redirect(redirect_url)

class ResultView(ListView):
    template_name = 'search/result.html'
    context_object_name = 'data_list'
    paginate_by = 20

    def get_queryset(self):
        # Get search query from session
        search_query = self.request.session.get('search_query', {})
        prompt = search_query.get('prompt', '')
        negative_prompt = search_query.get('negative_prompt', '')

        # Perform the search using query_maker
        query_maker = QueryMake()
        data_list = query_maker.query_to_elastic(prompt, negative_prompt)
        return data_list
    
    def post(self, request, *args, **kwargs):
        user_pk = request.user.pk
        prompt = request.POST.get('prompt', '')
        negative_prompt = request.POST.get('negative_prompt', '')
        prompt, negative_prompt = tokenizer(prompt, negative_prompt)

        if user_pk:
            prompt_log_check = Prompt_log.objects.filter(user_id=user_pk, prompt=prompt, negative_prompt=negative_prompt)

            if not prompt_log_check:
                plid = ""
                while True:
                    letters_set = string.ascii_letters
                    num = random.randrange(1, 9)
                    random_list = random.sample(letters_set, num)
                    random_str = f"PL{''.join(random_list)}"
                    try:
                        Prompt_log.objects.get(prompt_log_id=random_str)
                    except Prompt_log.DoesNotExist:
                        plid = random_str
                        break

                Prompt_log.objects.create(prompt_log_id=plid, user_id=user_pk, prompt=prompt, negative_prompt=negative_prompt)
            else:
                prompt_log_check[0].created_at = timezone.now()
                prompt_log_check[0].save()
        
        # Store the search results in the session
        request.session['search_query'] = {'prompt': prompt, 'negative_prompt': negative_prompt}
        
        # Build the URL for redirecting with pagination
        redirect_url = reverse('search:result')
        redirect_url += f'?page=1'
        
        # Redirect to ResultView with pagination
        return redirect(redirect_url)
    
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

def tokenizer(prompt,negative_prompt):
    #positive
    prompt=re.sub(r'[()\[\]{}]',',',prompt)
    tok = prompt.lower().split(',')
    temp_prompt = ""
    for tk in tok:
        tk=make_tokenizer(tk)
        if not tk:
            continue
        if "<" in tk or ">" in tk :
            continue
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
        if temp_prompt:
            temp_prompt=temp_prompt+","+tk
        else :
            temp_prompt=tk

    #negative
    negative_prompt = re.sub(r'[()\[\]{}]',',',negative_prompt)
    tok = negative_prompt.lower().split(',')
    temp_negative_prompt = ""
    for tk in tok:
        tk=make_tokenizer(tk)
        if not tk:
            continue
        if "<" in tk or ">" in tk :
            continue
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
        if temp_negative_prompt:
            temp_negative_prompt=temp_negative_prompt+","+tk
        else :
            temp_negative_prompt=tk
    return temp_prompt, temp_negative_prompt

def make_tokenizer(tk):
    if ":" in tk:
        i=tk.find(":")
        tk=tk[:i]
    return tk.strip()
'''
def make_ai(request):
    rank = QueryRank()
    ai_image = MakeImage()
    prompt_list = rank.index_data_to_elasticsearch("prompt")
    negative_prompt_list = rank.index_data_to_elasticsearch("negative_prompt")
    # 랜덤하게 5개 또는 6개의 키워드 선택
    num_keywords = random.randint(5, 6)
    selected_keywords = random.sample(prompt_list, num_keywords)
    # 선택한 키워드들을 하나의 문자열로 결합
    prompt_str = ','.join(keyword for keyword, _ in selected_keywords)+','
    print(prompt_str)
    
    selected_keywords = random.sample(negative_prompt_list, num_keywords)
    # 선택한 키워드들을 하나의 문자열로 결합
    negative_prompt_str = ','.join(keyword for keyword, _ in selected_keywords)+','
    print(negative_prompt_str)

    ai_image.prompt_make(prompt_str,negative_prompt_str)

    return render(request,"search/rank.html",{"prompt_list":prompt_list,"negative_list":negative_prompt_list})
'''
def rank(request):
    rank = QueryRank()
    prompt_list = rank.index_data_to_elasticsearch("prompt")
    negative_prompt_list = rank.index_data_to_elasticsearch("negative_prompt")
    return render(request,"search/rank.html",{"prompt_list":prompt_list,"negative_list":negative_prompt_list})