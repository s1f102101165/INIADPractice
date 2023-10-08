
from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('', views.index, name='index'), 
    path('chat', views.chat, name='chat'), 
    path('getchattest', views.view_comments, name='getchattest'), 
    
    path('api/getchatapi/', views.api_getchat),
    path('api/resetapi/', views.api_reset),
]
