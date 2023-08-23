from django.urls import path, include
from google_login_app.views import *

app_name = 'google_login_app'

urlpatterns = [
    path('google/login', google_login, name='google_login'),
    path('google/login/callback/', google_callback, name='google_callback'),
    path('google/login/finish/', GoogleLogin.as_view(), name='google_login_redirect'),
] 