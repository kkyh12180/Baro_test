from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.views.generic.list import MultipleObjectMixin

from search.elastic import Query
from search.models import Prompt
from follows.models import BookmarkPrompt

# Create your views here.
class PromptDetailView(DetailView, MultipleObjectMixin):
    model = Prompt
    context_object_name = 'target_prompt'
    template_name = 'prompts/detail.html'
    paginate_by = 25
    def get_context_data(self, **kwargs):
        query = Query()
        prompt=self.object
        user=self.request.user
        positive=self.request.session["positive"]
        if user.is_authenticated:
            bookmark=BookmarkPrompt.objects.filter(user=user,prompt=prompt,is_positive=positive)
        else:
            bookmark=None
        
        object_list=None
        #object_list=query.search_to_tag(prompt.prompt,positive)
        return super(PromptDetailView,self).get_context_data(object_list=object_list,bookmark=bookmark,**kwargs)

class PromptListView(ListView):
    model = Prompt
    context_object_name = 'prompt_list'
    template_name = 'prompts/list.html'
    paginate_by = 25