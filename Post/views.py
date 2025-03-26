from django.shortcuts import render
from .models import Question  # Импорт твоей модели вопросов

def index(request):
    questions = Question.objects.all().order_by('-date')  # Загружаем все вопросы из базы
    return render(request, 'index.html', {'questions': questions})

from django.shortcuts import render, get_object_or_404
from .models import Question, Answer

def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    answers = Answer.objects.filter(question=question)
    context = {
        'question': question,
        'answers': answers
    }
    return render(request, 'question.html', context)