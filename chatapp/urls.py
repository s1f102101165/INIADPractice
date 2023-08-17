from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'), 
    path('getchattest', views.getchattest, name='getchattest'), 
    
	path('api/getchatapi/', views.api_getchat),
]