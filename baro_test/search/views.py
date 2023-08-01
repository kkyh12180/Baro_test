from django.http import HttpResponse
from django.shortcuts import render
from search.search_in_elastic import query_to_elasticsearch

# Create your views here.
def main(request):
    return render(request,'search/main.html')

def test(request):
    data_list = query_to_elasticsearch()
    context = {'data_list': data_list}
    return render(request,'search/test.html',context)