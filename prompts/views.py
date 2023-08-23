from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView

from search.elastic import Query
from search.models import Prompt
from follows.models import BookmarkPrompt

# Create your views here.
class PromptDetailView(DetailView):
    model = Prompt
    context_object_name = 'target_prompt'
    template_name = 'prompts/detail.html'
    paginate_by = 25
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        query = Query()  # Create an instance of the Query class
        prompt = self.object
        user = self.request.user
        positive = self.request.GET.get('positive')
        
        if user.is_authenticated:
            bookmark = BookmarkPrompt.objects.filter(user=user, prompt=prompt, is_positive=(positive=='positive'))
        else:
            bookmark = None

        object_list = query.search_to_tag(prompt.prompt, positive)
        
        context['object_list'] = object_list
        context['bookmark'] = bookmark
        context['positive']=positive
        
        return context

class PromptListView(ListView):
    model = Prompt
    context_object_name = 'prompt_list'
    template_name = 'prompts/list.html'
    paginate_by = 25

#프롬프트에 북마크를 할  수 있다. 이미 북마크 상태이면 해제가 된다.
class PromptBookmarkView(RedirectView) :
    def get_redirect_url(self, *args, **kwargs) :
        return reverse('prompts:detail', kwargs={'positive':self.kwargs.get('positive'),'pk': self.request.GET.get('prompts_pk')})
    
    def get(self, request, *args, **kwargs) :
        prompt = get_object_or_404(Prompt, pk=self.request.GET.get('prompts_pk'))
        positive = ( self.request.GET.get('positive') == 'positive')
        user = self.request.user
        bookmark = BookmarkPrompt.objects.filter(user=user, prompt=prompt, is_positive=positive)

        if bookmark.exists() :
            bookmark.delete()
        else :
            BookmarkPrompt(user=user, prompt=prompt, is_positive=positive).save()

        return super(PromptBookmarkView, self).get(request, *args, **kwargs)