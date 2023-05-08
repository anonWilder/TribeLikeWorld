
from django.contrib import admin
from django.urls import path,include
from . import views

app_name = 'new'

urlpatterns = [
    path('', views.news, name="news"),
    path('news_detail/<id>/', views.news_detail, name='news_detail'),
]