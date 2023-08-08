from django.urls import path
from django.views.generic import TemplateView

from projects.views import *

app_name ="projects"

urlpatterns = [
    path('<str:pk>/',ProjectDetailView.as_view(), name='list'),
    path('create/',ProjectCrateView.as_view(), name='create'),
    path('delete/<str:pk>',ProjectDeleteView.as_view(), name='delete'),
    path('clear/',clear),
    
]