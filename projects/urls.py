from django.urls import path

from projects.views import *

app_name ="projects"

urlpatterns = [
    path('list/<str:pk>/',ProjectDetailView.as_view(), name='list'),
    path('create/',ProjectCreateView.as_view(), name='create'),
    path('delete/<str:pk>',ProjectDeleteView.as_view(), name='delete'),
]