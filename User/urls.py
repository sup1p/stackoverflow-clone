from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),   #bearer
    path('auth/logout/', views.logout, name='logout'),
    path('auth/user/', views.user, name='profile'),
]
