from django.urls import path
from django.views.generic import TemplateView

from search.views import *

app_name ="search"

urlpatterns = [
    path('',PromptLogListView.as_view(), name="home"),
    path('delete/',delete_all,name='delete_all'),
    path('delete/<str:pk>',delete,name='delete'),
]