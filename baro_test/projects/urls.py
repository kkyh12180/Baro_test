from django.urls import path
from django.views.generic import TemplateView

from projects.views import *

app_name ="projects"

urlpatterns = [
    path('list/',ProjectListView.as_view(), name='list'),
    path('create/',ProjectCrateView.as_view(), name='create'),
    path('detail/<str:pk>',ProjectDetailView.as_view(), name='detail'),
    path('delete/<str:pk>',ProjectDeleteView.as_view(), name='delete'),
    path('set/',ProjectSetView.as_view(),name='set'),
    path('clear/',clear),
    
]