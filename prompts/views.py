from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView

from search.elastic import Query
from search.models import Prompt, Prompt_log, Prompt_rank
from follows.models import BookmarkPrompt, PromptRecommend
from search.pocket import pocket

import openai
import re

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
    
class PromptRecommendView(ListView):
    model = PromptRecommend
    context_object_name = "recommend_list"
    template_name = "prompts/recommend.html"

    def get_queryset(self):
        user = self.request.user
        recommend_list = PromptRecommend.objects.filter(user=user).order_by('-id')
        return recommend_list

class RecommendView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('prompts:recommend_list')
    
    def get(self,request,*args,**kwargs):
        user=self.request.user
        try :
            similar_prompt, conflict_prompt = make_similar_conflict_prompt(user.pk)
            
            PromptRecommend(user=user,similar_prompt=similar_prompt,conflict_prompt=conflict_prompt).save()
        except Exception as e :
            print("error")
            print(e)
        return super(RecommendView,self).get(request,*args, **kwargs)
    
def make_similar_conflict_prompt(user_pk):
    user_log = Prompt_log.objects.filter(user_id=user_pk).order_by('?')[:8]

    # 로그 문자열들을 모은 리스트
    log_strings = [log.prompt for log in user_log]
    # 각 로그 문자열을 단어로 분리하고 쉼표로 조인하여 하나의 문자열로 만듦
    user_string = ','.join(' '.join(log.split()) for log in log_strings)

    openai.api_key = pocket().api_key

    query_set = Prompt_rank.objects.order_by('?')[:10]

    # 가져온 결과에서 prompt 필드만 추출
    prompt_list = list(query_set.values_list('prompt', flat=True))
    prompt_string = ','.join(' '.join(log.split()) for log in prompt_list)

    user_input = "("+user_string+")와 ("+prompt_string+")를 참고하여 비슷한 10개의 키워드만 한 줄로 작성해줘"
    messages=[
            {"role":"user","content":f"{user_input}"}
        ]
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages=messages
    )
    # ChatGPT 응답을 대화 내역에 추가
    similar_prompt = response.choices[0].message.content
    similar_prompt = rewrite(similar_prompt)

    user_input = "("+user_string+")와 ("+prompt_string+")를 참고하여 반대의 키워드만 한 줄로 작성해줘"
    messages=[
            {"role":"user","content":f"{user_input}"}
        ]
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages=messages
    )
    # ChatGPT 응답을 대화 내역에 추가
    conflict_prompt = response.choices[0].message.content
    conflict_prompt = rewrite(conflict_prompt)
    
    return similar_prompt, conflict_prompt

def rewrite(message):
    # 콜론(:) 이전의 부분을 선택
    keywords_part = message.split(":")[0]

    # 선택한 부분을 소문자로 변환
    lowercase_keywords_part = keywords_part.lower()

    # 소문자로 변환된 부분에서 숫자를 제거하고 단어만 추출
    words = re.findall(r'\b\w+\b', lowercase_keywords_part)

    # 단어들을 쉼표로 이어진 문자열로 변환
    result_string = ', '.join(words)

    return result_string
