from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from accounts.views import *

# app_name 명시
# 추후 accountapp:hello_world 로 접근이 가능해지기 때문
app_name = 'account'

urlpatterns = [
    # views.py의 hello_world 불러옴
    # path('mypage/<str:pk>', Mypage.as_view(), name='hello_world'),
    path('language/', ChangeLanguageView.as_view(), name='language'),
    path('signin/', LoginView.as_view(template_name='account/signin.html'), name='signin'),
    path('signup/', AccountCreateView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('mypage/<str:username>', AccountDetailView.as_view(), name='detail'),
    path('edit_info/<str:pk>', AccountUpdateView.as_view(), name='edit'),
    path('edit_password/<str:pk>', AccountPasswordUpdateView.as_view(), name='edit_password'),
    path('quit/<str:pk>', AccountDeleteView.as_view(), name='quit'),
    path('image/<str:username>',AccountImageListView.as_view(),name='image'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('adult/',ChangeAdultView.as_view(),name='adult'),
]