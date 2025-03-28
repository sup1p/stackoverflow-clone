from django.urls import path
from Post import views



urlpatterns = [
    path('questions/', views.questions_list_and_create, name='questions_list_and_create'),
    #get for list of q, post for creating q /\
    path('questions/<int:id>/', views.question_details_edit_delete, name='question_and_details_and_edit'),
    #edit for details of q, patch for editing q, delete for deleting q /\
    path('questions/<int:id>/vote/', views.question_vote, name='question_vote'),

    path('answers/', views.answer_list_create, name='answer_list_create'),
    #get for list of q, post for creating q
    path('answers/<int:id>/', views.answer_details_edit_delete, name='answer_and_details_and_edit'),
    # edit for details of ans, patch for editing ans, delete for deleting ans /\

    path('answers/<int:id>/vote/', views.answer_vote, name='answer_vote'),
    path('answers/<int:id>/accept/', views.answer_accept, name='answer_accept'),

    path('tags/', views.tags_list, name='tags_list'),
    path('tags/<int:id>/', views.tags_details, name='tag_details'),
    path('tags/name/<str:name>', views.tags_by_name, name='tags_by_name'),
    path('tags/search/', views.tags_search, name='tags_search'),
    path('tags/name/<str:name>/questions', views.tag_questions, name='tag_questions'),
]