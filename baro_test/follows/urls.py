from django.urls import path
from django.views.generic import TemplateView

from follows.views import *

app_name ="follows"

urlpatterns = [
    path('subscribe/',SubscriptionView.as_view(), name='subscribe'),
    path('subscribed/',SubscriptionListView.as_view(), name='subscribed'),
    path('follow',FollowView.as_view(), name='follow'),
    path('following/',FollowingListView.as_view(), name='following'),
    
    #path('bookmark/',BookmarkView.as_view(), name='bookmark'),
    #path('bookmarked/',BookmarkedListView.as_view(), name='bookmarked'),
    #path('liked/',LikedListView.as_view(), name='liked'),
    #path('like/',LikeListView.as_view(), name='like'),
]