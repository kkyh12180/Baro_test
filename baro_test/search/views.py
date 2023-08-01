from django.http import HttpResponse
from django.shortcuts import render
from search.search_in_elastic_lifeness import *

# Create your views here.
def main(request):
    if request.method == 'POST':
        prompt=request.POST.get('prompt','')
        negative_prompt = request.POST.get('negative_prompt','')
        context=result(prompt=prompt,negative_prompt=negative_prompt)
        return render(request,'search/test.html',context)
    return render(request,'search/main.html')

def test(request):
    query_maker=QueryMake()
    data_list = query_maker.query_to_elasticsearch()
    context = {'data_list': data_list}
    return render(request,'search/test.html',context)

def result(prompt,negative_prompt):
    query_maker=QueryMake()
    #positive prompt
    prompt=prompt.replace(', ',',')
    prompt_list=prompt.split(',')
    temp_prompt=""
    for prompt in prompt_list:
        if ' ' in prompt:
            query_maker.make_match_phrase("prompt",prompt)
        else :
            temp_prompt=temp_prompt+" "+str(prompt)
    query_maker.make_match("prompt",temp_prompt)

    #negative_prompt
    negative_prompt=negative_prompt.replace(', ',',')
    negative_prompt_list=negative_prompt.split(',')
    temp_negative_prompt=""
    for negative_prompt in negative_prompt_list:
        if ' ' in negative_prompt:
            query_maker.make_match_phrase("negative_prompt",negative_prompt)
        else :
            temp_negative_prompt=temp_negative_prompt+" "+str(negative_prompt)
    query_maker.make_match("negative_prompt",temp_negative_prompt)

    #prompt_search
    data_list=query_maker.search()
    context={'data_list':data_list}
    return context

