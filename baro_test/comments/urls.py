from django.urls import path
from django.views.generic import TemplateView

from comments.views import *

app_name ="comment"

urlpatterns = [
    path('create/',CommentCreateView.as_view(),name='create'),
    path('delete/<str:pk>',CommentDeleteView.as_view(),name='delete'),
]