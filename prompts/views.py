from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView

from search.elastic import Query
from search.models import Prompt
from follows.models import BookmarkPrompt

# Create your views here.
class PromptDetailView(ListView):
    context_object_name = 'data_list'
    template_name = 'prompts/detail.html'
    paginate_by = 25

    def get_queryset(self):
        # Perform the search using query_maker
        query = Query()  # Create an instance of the Query class
        prompt_id = self.kwargs['pk']
        positive = self.kwargs['positive']

        data_list = query.search_to_tag(prompt_id, positive)
        return data_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['target_prompt']=self.kwargs['pk']
        context['positive']=self.kwargs['positive']
        
        return context

class PromptListView(ListView):
    model = Prompt
    context_object_name = 'prompt_list'
    template_name = 'prompts/list.html'
    paginate_by = 24

    def get_queryset(self):
        positive = self.kwargs['positive']
        if positive=="prompt":
            prompt_list = Prompt.objects.filter(positive_weight__gte=50).order_by('-positive_weight')
        else:
            prompt_list = Prompt.objects.filter(negative_weight__gte=50).order_by('-negative_weight')
        return prompt_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #현재의 상태 가져오기
        positive = self.kwargs['positive']
        context['positive']=positive
        
        #자신이 최근에 북마크 한 데이터 가져오기
        bookmark_list = BookmarkPrompt.objects.filter(user=self.request.user,is_positive=(positive=='prompt'))
        bookmarked_prompt = [bookmark.prompt for bookmark in bookmark_list]
        context['bookmarked_prompt']=bookmarked_prompt

        return context

class BookmarkedPromptListView(ListView):
    model=Prompt
    context_object_name = "prompt_list"
    template_name="prompts/bookmark.html"
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user

        #현재의 상태 가져오기
        positive = self.kwargs['positive']

        #자신이 최근에 북마크 한 데이터 가져오기
        bookmarked_posts = BookmarkPrompt.objects.filter(user=user,is_positive=(positive=='prompt')).order_by('-bookmark_time')
        bookmarked_prompt = [bookmark.prompt for bookmark in bookmarked_posts]
        print(bookmarked_prompt)

        return bookmarked_prompt
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #현재의 상태 가져오기
        positive = self.kwargs['positive']
        context['positive']=positive

        return context

#프롬프트에 북마크를 할  수 있다. 이미 북마크 상태이면 해제가 된다.
class PromptBookmarkView(RedirectView) :
    def get_redirect_url(self, *args, **kwargs) :
        check = self.request.GET.get('list')
        if check:
            return reverse('prompts:bookmarked', kwargs={'positive':self.request.GET.get('positive')})
        return reverse('prompts:list', kwargs={'positive':self.request.GET.get('positive')})
    
    def get(self, request, *args, **kwargs) :
        prompt = get_object_or_404(Prompt, pk=self.request.GET.get('prompts_pk'))
        user = self.request.user
        
        #현재의 상태 가져오기
        positive = ( self.request.GET.get('positive') == 'prompt')
        bookmark = BookmarkPrompt.objects.filter(user=user, prompt=prompt, is_positive=positive)

        if bookmark.exists() :
            bookmark.delete()
        else :
            BookmarkPrompt(user=user, prompt=prompt, is_positive=positive).save()

        return super(PromptBookmarkView, self).get(request, *args, **kwargs)