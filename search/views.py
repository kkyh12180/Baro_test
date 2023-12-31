from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView
from django.utils import timezone

from search.elastic import Query
from search.models import *
from images.models import *

import string
import random
import re

#유저의 검색했던 로그를 5개, 랭크 10개 보여주기
class LogListView(ListView):
    template_name = 'search/main.html'
    context_object_name = 'log_list'

    # 유저의 검색 로그를 시간 순으로 5개 가져오기
    def get_queryset(self):
        user_pk = self.request.user.pk
        return Prompt_log.objects.filter(user_id=user_pk).order_by('-created_at')[:5]
    
    #랭크 10개 가져오기
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["prompt_rank"] = Prompt_rank.objects.filter(rank__lte=10)
        return context
    
    def post(self, request, *args, **kwargs):
        return result_page(request)

#검색 결과가 나오는 창
class ResultView(ListView):
    template_name = 'search/result.html'
    context_object_name = 'data_list'
    paginate_by = 20

    def get_queryset(self):
        # Get search query from session
        search_query = self.request.session.get('search_query', {})
        prompt = search_query.get('prompt', '')
        negative_prompt = search_query.get('negative_prompt', '')
        model_hash = search_query.get('model_hash', '')
        steps = search_query.get('steps', '')
        sampler = search_query.get('sampler', '')
        cfg_scale = search_query.get('cfg_scale', '')
        denoising_strength = search_query.get('denoising_strength', '')

        # Perform the search using query_maker
        query_maker = Query()
        data_list = query_maker.query_to_elastic(prompt, negative_prompt, model_hash, steps, cfg_scale, denoising_strength,sampler)
        return data_list
    
    #검색 결과 창에서 재검색을 실행시 코드
    def post(self, request, *args, **kwargs):
        return result_page(request)

#검색 창에서 검색 실행
def result_page(request):
    user_pk = request.user.pk
    prompt = request.POST.get('prompt', '')
    negative_prompt = request.POST.get('negative_prompt', '')
    model_hash = request.POST.get('model_hash','')
    steps = request.POST.get('steps','')
    cfg_scale = request.POST.get('cfg_scale','')
    denoising_strength = request.POST.get('denoising_strength','')
    sampler = request.POST.get('sampler','')
    #검색 결과를 토큰화
    prompt, negative_prompt = tokenizer(prompt, negative_prompt)

    #user가 존재한다면 검색로그에 추가
    if user_pk and (prompt or negative_prompt):
        prompt_log_check = Prompt_log.objects.filter(user_id=user_pk, prompt=prompt, negative_prompt=negative_prompt)

        #해당 prompt를 처음 검색하면 새로운 Promp_log를 생성
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
        else: #이미 같은 내용을 검색한 기록이 있으면 시간을 변경
            prompt_log_check[0].created_at = timezone.now()
            prompt_log_check[0].save()
    
    # 검색 내용을 session에 저장
    request.session['search_query'] = {
        'prompt': prompt,
        'negative_prompt': negative_prompt,
        'model_hash': model_hash,
        'steps': steps,
        'cfg_scale': cfg_scale,
        'denoising_strength': denoising_strength,
        'sampler': sampler,
    }
    
    # Build the URL for redirecting with pagination
    redirect_url = reverse('search:result')
    redirect_url += f'?page=1'
    
    # Redirect to ResultView with pagination
    return redirect(redirect_url)

#user가 가지고 있는 모든 prompt_log를 찾아서 제거
def delete_all(request):
    user_pk=request.user.pk
    log_list = Prompt_log.objects.filter(user_id=user_pk)
    for log in log_list:
        log.delete()
    return redirect('search:home')

#해당 prompt_log를 삭제
def delete(request, pk):
    user_pk=request.user.pk
    log_list = Prompt_log.objects.filter(user_id=user_pk,prompt_log_id=pk)
    for log in log_list:
        log.delete()
    return redirect('search:home')

def tokenizer(prompt,negative_prompt):
    #positive

    #<>를 제외한 모든 괄호를 제거하고 ','를 기준으로 분리
    prompt=re.sub(r'[()\[\]{}]',',',prompt)
    prompt=re.sub(r'[_\-=+#/\?^.@*\"※~ㆍ!\']',' ',prompt)
    tok = prompt.lower().split(',')

    temp_prompt = ""
    for tk in tok:
        tk=make_tokenizer(tk)
        temp_tk=tk.replace(" ","")
        try:
            float(temp_tk)
            continue
        except:
            if not tk:
                continue
            if "<" in tk or ">" in tk or tk=="lora":
                continue
        #prompt가 존재할 경우 가중치 증가, 없을 경우 생성 후 가중치 증가
        prompt = Prompt.objects.filter(prompt=tk)
        if not prompt:
            prompt_temp=Prompt()
            prompt_temp.prompt=tk
            prompt_temp.positive_weight=0
        else:
            prompt_temp = prompt[0]
        prompt_temp.positive_weight=prompt_temp.positive_weight+1
        prompt_temp.save()

        #prompt를 정제하여 저장
        if temp_prompt:
            temp_prompt=temp_prompt+","+tk
        else :
            temp_prompt=tk

    #negative

    #<>를 제외한 모든 괄호를 제거하고 ','를 기준으로 분리
    negative_prompt=re.sub(r'[()\[\]{}]',',',negative_prompt)
    negative_prompt=re.sub(r'[_\-=+#/\?^.@*\"※~ㆍ!\']',' ',negative_prompt)
    tok = negative_prompt.lower().split(',')

    temp_negative_prompt = ""
    for tk in tok:
        tk=make_tokenizer(tk)
        temp_tk=tk.replace(" ","")
        try:
            float(temp_tk)
            continue
        except:
            if not tk:
                continue
            if "<" in tk or ">" in tk or tk=="lora":
                continue
        #prompt가 존재할 경우 가중치 증가, 없을 경우 생성 후 가중치 증가
        prompt = Prompt.objects.filter(prompt=tk)
        if not prompt:
            prompt_temp=Prompt()
            prompt_temp.prompt=tk
            prompt_temp.negative_weight=0
        else:
            prompt_temp = prompt[0]
        prompt_temp.negative_weight=prompt_temp.negative_weight+1
        prompt_temp.save()

        #prompt를 정제하여 저장
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
