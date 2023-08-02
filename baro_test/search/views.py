from django.http import HttpResponse
from django.shortcuts import render
from search.search_in_elastic import *
from search.logs import *

# Create your views here.
def main(request):
    if request.method == 'POST':
        prompt=request.POST.get('prompt','')
        negative_prompt = request.POST.get('negative_prompt','')
        context=result(prompt=prompt,negative_prompt=negative_prompt)
        return render(request,'search/result.html',context)
    return render(request,'search/main.html')

def test(request):
    logs()
    return render(request,'search/main.html')

def result(prompt,negative_prompt):
    query_maker=QueryMake()
    data_list=query_maker.query_to_elastic(prompt,negative_prompt)
    context={'data_list':data_list}
    return context