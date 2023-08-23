from django.urls import path

from prompts.views import *

app_name ="prompts"

urlpatterns = [
    path('list/<str:positive>',PromptListView.as_view(), name='list'),
    path('detail/<str:pk>/<str:positive>',PromptDetailView.as_view(), name='detail'),
    path('bookmark/', PromptBookmarkView.as_view(), name='bookmark'),
    path('bookmarked/<str:positive>', BookmarkedPromptListView.as_view(), name='bookmarked'),
]