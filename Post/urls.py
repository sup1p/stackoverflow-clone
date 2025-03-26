from django.urls import path
from . import views

urlpatterns = [
    path('questions/<int:question_id>/', views.question_detail, name='question_detail'),
]
