from django.contrib import admin
from django.urls import path
from User.views import LoginView 

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'), 
]
