from django.contrib import admin
from django.urls import path, include
from images.views import ImagePostCreateView, ImagePostListView, ImagePostDetailView, ImagePostDeleteView, ImagePostUpdateView

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
]