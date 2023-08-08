from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from account.views import AccountCreateView, AccountDetailView, AccountUpdateView, AccountPasswordUpdateView, AccountDeleteView

# app_name 명시
# 추후 accountapp:hello_world 로 접근이 가능해지기 때문
app_name = 'account'

urlpatterns = [
    # views.py의 hello_world 불러옴
    # path('mypage/<str:pk>', Mypage.as_view(), name='hello_world'),
    path('signin/', LoginView.as_view(template_name='account/signin.html'), name='signin'),
    path('signup/', AccountCreateView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('mypage/<str:username>', AccountDetailView.as_view(), name='detail'),
    path('edit_info/<str:pk>', AccountUpdateView.as_view(), name='edit'),
    path('edit_password/<str:pk>', AccountPasswordUpdateView.as_view(), name='edit_password'),
    path('quit/<str:pk>', AccountDeleteView.as_view(), name='quit'),
]