from django.urls import path
from django.views.generic import TemplateView

from search.views import *

app_name ="search"

urlpatterns = [
    path('',hello_world, name="home"),
]