from django.urls import path
from . import views

urlpatterns = [
    path('questions/<int:question_id>/', views.question_detail, name='question_detail'),
    path('question/<int:post_id>/', views.question_detail, name='post_detail'),
    path('question/ask', views.create_question, name='ask_question'),
    path('questions/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('questions/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('tag-suggestions/', views.tag_suggestions, name='tag_suggestions'),
    path('question/<int:question_id>/add-answer/', views.create_answer, name='add_answer'),
    path('answers/<int:answer_id>/edit/', views.edit_answer, name='edit_answer'),
    path('answers/<int:answer_id>/delete/', views.delete_answer, name='delete_answer'),
    path('question/<int:question_id>/vote/', views.vote_question, name='vote_question'),
]
