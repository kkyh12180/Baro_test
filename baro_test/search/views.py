from django.http import HttpResponse
from django.shortcuts import render
from search.search_in_elastic import *
from search.logs import *

# Create your views here.
def main(request):
    if request.method == 'POST':
        prompt=request.POST.get('prompt','')
        negative_prompt = request.POST.get('negative_prompt','')
        print(request.user.pk)
        if request.user != "AnonyomousUser":
            temp_log = LogClass()
            temp_log.log_data(prompt,negative_prompt,request.user.pk)
            temp_log.logs(request.user.pk)
        context=result(prompt=prompt,negative_prompt=negative_prompt)
        return render(request,'search/result.html',context)
    return render(request,'search/main.html')

def test(request):
    temp_log=LogClass()
    temp_log.logs()
    return render(request,'search/main.html')

def result(prompt,negative_prompt):
    query_maker=QueryMake()
    data_list=query_maker.query_to_elastic(prompt,negative_prompt)
    context={'data_list':data_list}
    return context