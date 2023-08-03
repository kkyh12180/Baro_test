from django.urls import path
from django.views.generic import TemplateView

from search.views import *

app_name ="search"

urlpatterns = [
    path('',main, name="home"),
    path('test/',test,name='test'),
    path('log/',LogListView.as_view(),name='log'),
    path('delete/',delete,name='delete'),
]