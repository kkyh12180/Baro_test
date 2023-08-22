from django.urls import path

from comments.views import *

app_name ="comment"

urlpatterns = [
    path('create/<str:pk>',CommentCreateView.as_view(),name='create'),
    path('delete/<str:pk>',CommentDeleteView.as_view(),name='delete'),
    path('image_comment_like/', CommentImagePostLikeView.as_view(), name='image_comment_like'),
]