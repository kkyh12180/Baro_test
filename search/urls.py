from django.urls import path
from django.views.generic import TemplateView

from search.views import *

app_name ="search"

urlpatterns = [
    path('',SearchListView.as_view(), name="home"),
    path('delete/',delete_all,name='delete_all'),
    path('delete/<str:pk>',delete,name='delete'),
    path('result/',ResultView.as_view(), name="result"),
    path('chat/',chat_view,name="chat_view"),
    path('rank/',rank,name="rank"),
]