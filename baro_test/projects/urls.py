from django.urls import path
from django.views.generic import TemplateView

from projects.views import *

app_name ="projects"

urlpatterns = [
    path('list/',ProjectListView.as_view(), name='list'),
    path('create/',ProjectCrateView.as_view(), name='create'),
    #TODO 공지사항은 고정 GID 사용 필요
    #path('detail/GRTh',AnnouncementView.as_view(),name='announcement'),
    path('detail/<str:pk>',ProjectDetailView.as_view(), name='detail'),
    path('delete/<str:pk>',ProjectDeleteView.as_view(), name='delete'),
    path('clear/',clear),
    
]