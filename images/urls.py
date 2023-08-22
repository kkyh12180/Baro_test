from django.urls import path

from images.views import *

# app_name 명시
app_name = 'images'

urlpatterns = [
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