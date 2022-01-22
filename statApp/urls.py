from django.urls import path
from . import views
# from .views import *


urlpatterns = [
    path('', views.index),
    path('weather/', views.IndexPage.as_view(), name='weather'),
]
