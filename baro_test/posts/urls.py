from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from posts.views import *

# app_name 명시
app_name = 'post'

urlpatterns = [
    path('',PostListView.as_view(), name='list'),
    path('create/',PostCrateView.as_view(), name='create'),
    path('detail/<str:pk>',PostDetailView.as_view(), name='detail'),
    path('update/<str:pk>',PostUpdateView.as_view(), name='update'),
    path('delete/<str:pk>',PostDeleteView.as_view(), name='delete'),
    path('clear',clear),
    path('like', PostLikeView.as_view(), name='like'),
]