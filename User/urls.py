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
    path('users/me/', views.user_edit_get, name='user_edit_get'),
    path('users/<int:id>/questions/', views.user_questions, name='user_questions'),
    path('users/<int:id>/answers/', views.user_answers, name='user_answers'),
    path('users/<int:id>/tags/', views.user_tags, name='user_tags'),
    path('users/<int:id>/reputation/', views.user_reputation_history, name='user_reputation_history'),
]
