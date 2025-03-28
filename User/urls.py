from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),   #bearer
    path('auth/logout/', views.logout, name='logout'),
    path('auth/user/', views.user, name='profile'),

    path('users/', views.user_list, name='users'),
    path('users/<int:id>/', views.user_details, name='user_details'),
    path('users/me/', views.user_edit, name='user_edit'),
]
