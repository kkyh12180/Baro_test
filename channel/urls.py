from django.urls import path

from channel.views import *

# app_name 명시
app_name = 'channel'

urlpatterns = [
    path('create/',ChannelCreateView.as_view(), name='create'),
    path('detail/<str:pk>',ChannelDetailView.as_view(), name='detail'),
    path('update/<str:pk>',ChannelUpdateView.as_view(), name='update'),
    path('delete/<str:pk>',ChannelDeleteView.as_view(), name='delete'),
    path('like/', ChannelLikeView.as_view(), name='like'),
]