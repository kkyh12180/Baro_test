from django.urls import path

from search.views import *

app_name ="search"

urlpatterns = [
    path('',LogListView.as_view(), name="home"),
    path('delete/',delete_all,name='delete_all'),
    path('delete/<str:pk>',delete,name='delete'),
    path('result/',ResultView.as_view(), name="result"),
    #path('make_ai/',make_ai,name="make_ai"),
    path('rank/',rank,name="rank"),
]