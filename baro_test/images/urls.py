from django.contrib import admin
from django.urls import path, include
from images.views import *

# app_name 명시
# 추후 accountapp:hello_world 로 접근이 가능해지기 때문
app_name = 'images'

urlpatterns = [
    # views.py의 hello_world 불러옴
    # path('mypage/<str:pk>', Mypage.as_view(), name='hello_world'),
    path('', ImagePostListView.as_view(), name='list'),
    path('create/', ImagePostCreateView.as_view(), name='create'),
    path('detail/<str:pk>', ImagePostDetailView.as_view(), name='detail'),
    path('delete/<str:pk>', ImagePostDeleteView.as_view(), name='delete'),
    path('update/<str:pk>', ImagePostUpdateView.as_view(), name='update'),
    path('like/', ImagePostLikeView.as_view(), name='like'),
    path('subscribe/',ImagePostSubscribeView.as_view(),name='subscribe'),
    path('adult/',ImagePostAdultView.as_view(),name='adult'),
    path('bookmark/', ImagePostBookmarkView.as_view(), name='bookmark'),
    path('exif_input/<str:pk>', InputExifInfo.as_view(), name='input_exif'),
]