from logging import raiseExceptions

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from User.models import CustomUser
from .forms import QuestionCreationForm, QuestionEditForm, AnswerCreationForm, AnswerEditForm
from .models import Question, Tag, QuestionVote  # Импорт твоей модели вопросов

def index(request):
    questions = Question.objects.all().order_by('-created_at')  # Загружаем все вопросы из базы
    return render(request, 'index.html', {'questions': questions})

from django.shortcuts import render, get_object_or_404
from .models import Question, Answer

def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if question.author != request.user:
        question.views += 1
    question.save()
    answers = Answer.objects.filter(question=question)
    context = {
        'question': question,
        'answers': answers
    }
    return render(request, 'question.html', context)

@login_required(login_url='login')
def create_question(request):
    if request.method == 'POST':
        form = QuestionCreationForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()

            tags = form.cleaned_data.get('tags')
            tags_list = tags.split(',')
            for tag_name in tags_list:
                try:
                    tag = Tag.objects.get(name=tag_name)
                    question.tags.add(tag)
                except Tag.DoesNotExist:
                    pass

            messages.success(request, 'Question successfully created!')
            return redirect('question_detail', question_id=question.id)
    else:
        form = QuestionCreationForm()
        context = {
            'form': form
        }
        return render(request, 'ask.html', context)

def tag_suggestions(request):
    if request.method == "GET":
        query = request.GET.get('q', '')
        tags = Tag.objects.filter(name__icontains=query).values_list('name', flat=True)
        return JsonResponse(list(tags), safe=False)


@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if question.author != request.user:
        messages.error(request, 'It is not your question.')
        return redirect('question_detail', question_id=question.id)

    if request.method == 'POST':
        form = QuestionEditForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)

            tags = form.cleaned_data.get('tags')
            tags_list = tags.split(',')

            question.tags.clear()

            for tag_name in tags_list:
                try:
                    question.tags.add(Tag.objects.get(name=tag_name))
                except Tag.DoesNotExist:
                    pass

            question.save()
            messages.success(request, 'Question successfully updated!')
            return redirect('question_detail', question_id=question.id)
    else:
        form = QuestionEditForm(instance=question)

    context = {'form': form, 'question': question}
    return render(request, 'edit_question.html', context)


@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST' and question.author == request.user:
        question.delete()
        messages.success(request, 'Question successfully deleted.')
        messages.success(request, 'Question successfully deleted.')
        return redirect('index')
    messages.error(request, 'It is not your question.')
    return redirect('question_detail', question_id=question.id)


@login_required
def create_answer(request,question_id):
    if request.method == 'POST':
        form = AnswerCreationForm(request.POST)
        question = Question.objects.get(id=question_id)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.question = question
            answer.save()
            messages.success(request, 'Answer successfully posted!')
            return redirect('question_detail', question_id=question.id)
        else:
            messages.error(request, 'Error posting the answer.')
    else:
        form = AnswerCreationForm()
        context = {
            'form': form
        }
        return render(request, 'question.html', context)

@login_required()
def edit_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    question = answer.question
    if answer.author == request.user:
        if request.method == 'POST':
            form = AnswerEditForm(request.POST, instance=Answer.objects.get(id=answer_id))
            if form.is_valid():
                answer.save()
                form.save()
                messages.success(request, 'Answer successfully updated!')
                return redirect('question_detail', question_id=question.id)
            else:
                messages.error(request, 'Error updating the answer.')
        else:
            form = AnswerCreationForm()
            context = {
                'form': form,
                'question' : question
            }
            return render(request, 'edit_answer.html', context)
    messages.error(request, 'It is not your answer.')
    return redirect('question_detail', question_id=question.id)

@login_required
def delete_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    question = answer.question
    if request.method == 'POST' and answer.author == request.user:
        answer.delete()
        messages.success(request, 'Answer successfully deleted.')
    else:
        messages.error(request, 'It is not your answer.')
    return redirect('question_detail', question_id=question.id)


@login_required
def vote_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == "POST":
        vote_type = request.POST.get("vote_type")
        value = 1 if vote_type == "upvote" else -1

        # Проверяем, существует ли уже голос этого пользователя для данного вопроса
        try:
            vote = QuestionVote.objects.get(user=request.user, question=question)
            if vote.value == value:
                # Если пользователь пытается проголосовать так же, то отменяем голос
                vote.delete()
                question.score -= value
            else:
                # Если пользователь изменяет голос с upvote на downvote или наоборот
                question.score += 2 * value
                vote.value = value
                vote.save()
        except QuestionVote.DoesNotExist:
            # Если пользователь ещё не голосовал за данный вопрос
            QuestionVote.objects.create(user=request.user, question=question, value=value)
            question.score += value

        question.save()
        return JsonResponse({"score": question.score})